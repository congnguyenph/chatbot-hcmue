from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from rag_engine import RAGEngine

load_dotenv()
app = Flask(__name__)
CORS(app)

rag_engine = RAGEngine()
chat_history = []  # Lưu trữ lịch sử trò chuyện

@app.route("/")
def index():
    return render_template("messenger_chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400
    
    # Gọi RAGEngine với lịch sử trò chuyện
    answer = rag_engine.get_answer(question, chat_history)
    
    # Cập nhật lịch sử trò chuyện
    chat_history.append((question, answer))
    if len(chat_history) > 10:  # Giới hạn 10 lượt
        chat_history.pop(0)
    
    return jsonify({"answer": answer, "history": chat_history})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)