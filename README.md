# 🤖 Chatbot HCMUE – Công tác sinh viên

Chatbot trả lời câu hỏi về công tác sinh viên tại Trường Đại học Sư phạm TP.HCM (HCMUE), sử dụng kết hợp giữa tìm kiếm embedding và API LLM từ OpenRouter.

---

## 🚀 Tính năng chính

- Trả lời theo dữ liệu tĩnh từ file `qa-ctsv.json`
- Nếu không tìm thấy câu hỏi tương tự, chatbot sẽ hỏi LLM qua OpenRouter API
- Giao diện web đơn giản, dễ sử dụng
- Có ghi log các phiên hỏi–đáp

---

## 🧱 Công nghệ sử dụng

- Flask + Flask-CORS
- Sentence-Transformers (MiniLM)
- OpenAI SDK (dùng cho OpenRouter)
- HTML + JS frontend

---

## 📁 Cấu trúc thư mục
.
├── app.py # Flask backend
├── qa_engine.py # Logic xử lý câu hỏi + gọi LLM
├── requirements.txt # Thư viện cần cài
├── render.yaml # (tuỳ chọn) cấu hình auto deploy Render
├── .env # Chứa OPENROUTER_API_KEY (không public)
├── data/
│ └── qa-ctsv.json # Dữ liệu Q&A tĩnh
└── templates/
  └── messenger_chat.html # Giao diện người dùng


---

## 💻 Chạy local

```bash
# 1. Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Hoặc .\venv\Scripts\activate nếu dùng Windows

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Tạo file .env
echo OPENROUTER_API_KEY=sk-... > .env

# 4. Chạy ứng dụng
python app.py

Truy cập: http://localhost:5000/