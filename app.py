from flask_cors import CORS
from dotenv import load_dotenv
from rag_engine import RAGEngine
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

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

    answer = rag_engine.get_answer(question, chat_history)
    chat_history.append((question, answer))
    if len(chat_history) > 10:
        chat_history.pop(0)

    chat_entry = {
        "time": datetime.now().isoformat(timespec='seconds'),
        "question": question,
        "answer": answer
    }
    with open("chat_logs.json", "a", encoding="utf-8") as f:
        json.dump(chat_entry, f, ensure_ascii=False)
        f.write("\n")

    return jsonify({"answer": answer, "history": chat_history})

@app.route("/admin_panel")
def admin_panel():
    return render_template("admin_panel.html")

@app.route("/login_api", methods=["POST"])
def login_api():
    data = request.get_json()
    if data["username"] == os.getenv("ADMIN_USER") and data["password"] == os.getenv("ADMIN_PASS"):
        session["admin"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Sai tài khoản hoặc mật khẩu."})

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin_panel")

UPLOAD_FOLDER = './pdf_documents'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    file = request.files['pdf_file']
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        # xử lý tiếp nếu cần
        return jsonify({"message": f"Đã lưu vào {save_path}"}), 200
    return jsonify({"message": "File không hợp lệ"}), 400

@app.route("/chat_logs")
def chat_logs():
    if not session.get("admin"):
        return jsonify([])
    try:
        with open("chat_logs.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
        return jsonify([json.loads(line.strip()) for line in lines])
    except:
        return jsonify([])
@app.route("/pdf_list")
def pdf_list():
    pdf_folder = "pdf_documents"  # hoặc chỉnh lại nếu bạn dùng đường dẫn khác
    if not os.path.exists(pdf_folder):
        return jsonify([])

    files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    return jsonify(files)


if __name__ == "__main__":
    print("🔗 Chatbot đang chạy tại: http://localhost:5000")
    print("🔗 Trang Quản trị Chatbot đang chạy tại: http://localhost:5000/admin_panel")
    app.run(debug=False, host="0.0.0.0", port=5000)
