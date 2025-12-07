import ollama

response = ollama.chat(
    model="gemma3:4b",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

print(response)
