from flask import Flask, request, jsonify
from qa_engine import QAEngine
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
qa_engine = QAEngine("data/qa_1000_cong_tac_sinh_vien_hcmue.json")

@app.route("/")
def home():
    return "✅ Chatbot HCMUE (Embedding + DeepSeek) is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' field"}), 400
    answer = qa_engine.get_answer(data["question"])
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
