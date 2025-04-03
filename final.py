import os
import base64
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
token = os.getenv("TOKEN")

if not token:
    raise ValueError("TOKEN not found in environment variables.")

endpoint = "Azure endpoint"
model_name = "gpt-4o-mini"

# Initialize OpenAI client
client = OpenAI(base_url=endpoint, api_key=token)

def get_image_data_url(image_file: str, image_format: str) -> str:
    """Converts an image file to a data URL string."""
    with open(image_file, "rb") :
        image_data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{image_format};base64,{image_data}"

# Initialize Flask app
app = Flask(__name__)

# Serve the chatbot UI
@app.route("/")
def index():
    return render_template("final.html")

# API route for chatbot with image analysis
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")
    image = request.files.get("image")

    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    if user_message:
        conversation.append({"role": "user", "content": user_message})
    
    if image:
        image_path = os.path.join("uploads", image.filename)
        image.save(image_path)
        image_url = get_image_data_url(image_path, "jpg")
        conversation.append({"role": "user", "content": [
            {"type": "text", "text": user_message if user_message else "What's in this image?"},
            {"type": "image_url", "image_url": {"url": image_url}},
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
    except Exception :
        bot_reply = f"Error: {str(e)}"
    
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
