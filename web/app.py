from flask import Flask, render_template, request
from markupsafe import Markup
import requests
import subprocess
from flask import jsonify 
import ollama
import json
import re



app = Flask(__name__)


# Load custom knowledge once at startup
try:
    with open("custom_knowledge.txt", "r", encoding="utf-8") as f:
        CUSTOM_KNOWLEDGE = f.read()
except Exception as e:
    CUSTOM_KNOWLEDGE = ""
    print(f"Error loading custom knowledge: {e}")

@app.route("/")
def home():
    user = "Kenneth"
    return render_template("index.html", name=user)

@app.route("/hello/<username>")
def hello(username):
    return f"<h2>Hello {username} from URL route!</h2>"

@app.route("/redirect-user")
def redirect_user():
    return redirect(url_for("hello", username="FlaskUser"))

@app.route("/greet", methods=["POST"])
def greet():
    name = request.form.get("user")
    return render_template("greet.html", username=name)







#AI Generate Website

@app.route("/ask", methods=["GET", "POST"])
def ask():
    explanation = ""
    preview_html = ""  # ← Plain string, NOT Markup()

    if request.method == "POST":
        prompt = request.form.get("prompt")

        try:
            response = ollama.chat(
                model="gemma3:4b",
                messages=[
                    {"role": "system", "content": CUSTOM_KNOWLEDGE or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw = response['message']['content']
            print("Raw AI response:\n", raw)

            # --- Extract JSON safely ---
            text = raw.strip()
            text = re.sub(r"^```json\s*|```$", "", text, flags=re.MULTILINE)

            start = text.find("{")
            end = text.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found")

            json_part = text[start:end]
            data = json.loads(json_part)

            explanation = data.get("explanation", "No explanation provided.")
            html_from_ai = data.get("html", "").strip()

            if html_from_ai:
                # Extract <style> if exists
                style_match = re.search(r"<style.*?>.*?</style>", html_from_ai, re.DOTALL | re.IGNORECASE)
                style = style_match.group(0) if style_match else ""

                # Remove <style> from body
                body = re.sub(r"<style.*?>.*?</style>", "", html_from_ai, re.DOTALL | re.IGNORECASE).strip()

                # Build complete valid HTML
                full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
    {style}
</head>
<body>
    {body}
</body>
</html>"""

                # IMPORTANT: Just store as plain string (NO Markup, NO escaping tricks)
                preview_html = full_html

            else:
                explanation += " (AI returned no HTML)"

        except Exception as e:
            explanation = f"Error: {str(e)}<br><pre>{raw[:800]}</pre>"

    return render_template(
        "ask.html",
        response=explanation,
        page_html=preview_html  # ← plain string
    )

if __name__ == "__main__":
    app.run(debug=True)