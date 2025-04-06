import os
from flask import Flask, request, render_template, jsonify, send_from_directory, url_for
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables.")

# OpenAI or Azure endpoint and model
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4-vision-preview"  # Use a model that supports vision

client = OpenAI(base_url=endpoint, api_key=token)

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("final.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")
    image = request.files.get("image")

    conversation = [{"role": "system", "content": "You are a helpful assistant."}]

    if user_message and not image:
        conversation.append({"role": "user", "content": user_message})

    if image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_path)

        # Construct full URL based on Render-hosted domain
        render_host = request.url_root.rstrip("/")
        image_url = f"{render_host}/uploads/{image.filename}"

        conversation.append({"role": "user", "content": [
            {"type": "text", "text": user_message or "What's in this image?"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]})

    try:
        response = client.chat.completions.create(
            messages=conversation,
            model=model_name,
            temperature=1.0,
            max_tokens=1000,
            top_p=1.0
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
