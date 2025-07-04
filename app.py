from flask import Flask, request, jsonify
from flask_cors import CORS
from qa_engine import QAEngine
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

qa_engine = QAEngine("data/qa-ctsv.json")

@app.route("/")
def home():
    return "✅ Chatbot HCMUE is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")
    level = data.get("level")
    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400
    answer = qa_engine.get_answer(question, level)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
