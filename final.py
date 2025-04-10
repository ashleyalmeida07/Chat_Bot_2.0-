import os
import base64
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

# Load environment variables
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

# Initialize Azure OpenAI client
client = OpenAI(base_url=endpoint, api_key=token)

def get_image_data_url(image_path: str, image_format: str = "jpg") -> str:
    """Convert image file to base64 data URL with a specified format."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{image_format};base64,{image_data}"

@app.route('/')
def index():
    return render_template('final.html')  # Make sure your form supports image and message input

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get("message")
    image = request.files.get("image")

    conversation = [{"role": "system", "content": "You are a helpful assistant."}]

    if image and image.filename:
        image_path = os.path.join("uploads", image.filename)
        image.save(image_path)
        image_url = get_image_data_url(image_path, "jpg")

        conversation.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message if user_message else "What's in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        })
    elif user_message:
        conversation.append({"role": "user", "content": user_message})
    else:
        return jsonify({"reply": "Please provide a message or an image."})

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

if __name__ == '__main__':
    app.run(debug=True)
