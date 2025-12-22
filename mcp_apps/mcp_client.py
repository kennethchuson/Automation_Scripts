# mcp_client.py
import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


OLLAMA_MODEL = "llama3.2:latest"   

async def run_client():
    # Launch the MCP server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Discover all available tools
            tools_response = await session.list_tools()
            tools = tools_response.tools

            print("\n=== Connected to MCP Server ===")
            print(f"Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  • {tool.name} — {tool.description}")
            print("=" * 40)

            while True:
                user_query = input("\nEnter your query (or 'quit' to exit): ").strip()
                if user_query.lower() in {"quit", "exit", "bye"}:
                    print("Goodbye!")
                    break
                if not user_query:
                    continue

                # Message history for Ollama
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful, precise assistant with access to tools. "
                            "Always use the 'current_time' tool when asked for the time or date. "
                            "Use 'add' or 'multiply' for math. Use file tools for reading/writing files. "
                            "Never guess the time — always call the tool."
                        )
                    },
                    {"role": "user", "content": user_query}
                ]

                # First call: ask Ollama (with tool definitions)
                response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=messages,
                    tools=[tool.model_dump() for tool in tools],
                )

                message = response["message"]
                assistant_text = message.get("content", "")
                if assistant_text:
                    print(f"\nAssistant: {assistant_text}")

                # Handle any tool calls
                if "tool_calls" in message:
                    for tool_call in message["tool_calls"]:
                        func_name = tool_call["function"]["name"]
                        args = tool_call["function"]["arguments"]
                        print(f"\n🔧 Using tool: {func_name} with args → {args}")

                        # Call the tool via MCP
                        result = await session.call_tool(func_name, args)

                        # Extract text content from the result
                        content_text = ""
                        if result.content:
                            for part in result.content:
                                if part.type == "text":
                                    content_text += part.text

                        # Append tool result to conversation
                        messages.append(message)  # the assistant's tool call message
                        messages.append({
                            "role": "tool",
                            "content": content_text or "Tool executed (no text output)",
                            "name": func_name
                        })

                    # Final call: let Ollama summarize/use the tool results
                    final_response = ollama.chat(
                        model=OLLAMA_MODEL,
                        messages=messages,
                        tools=[tool.model_dump() for tool in tools],
                    )
                    final_text = final_response["message"]["content"]
                    print(f"\nFinal Answer: {final_text}")
                print("\n" + "—" * 50)

if __name__ == "__main__":
    print("Starting MCP + Ollama client...")
    print(f"Using model: {OLLAMA_MODEL}")
    print("Tip: Pull a strong model with: ollama pull qwen2.5:7b")
    asyncio.run(run_client())