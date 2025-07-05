Chatbot HCMUE
Hệ thống chatbot hỗ trợ sinh viên Trường Đại học Sư phạm TP.HCM, trả lời các thắc mắc liên quan đến công tác sinh viên, học phí, học bổng, rèn luyện, chính sách và quy định nhà trường dựa trên tài liệu PDF chính thức.

**Tính năng**

- Xử lý cả PDF dạng text và PDF quét (OCR).
- Tích hợp tìm kiếm ngữ nghĩa với mô hình embeddings tiếng Việt (thanhtantran/Vietnamese_Embedding_v2).
- Sử dụng API Gemini để tạo câu trả lời tự nhiên.
- Giao diện web thân thiện với lịch sử trò chuyện.
- Logging chi tiết để theo dõi xử lý PDF và truy vấn người dùng.

**Yêu cầu hệ thống**

- Python: 3.8 hoặc cao hơn
- Tesseract OCR: Cài đặt để hỗ trợ xử lý PDF quét (Hướng dẫn cài đặt)
- Poppler: Yêu cầu cho pdf2image (Hướng dẫn cài đặt)
- Hệ điều hành: Windows, Linux, hoặc macOS
- Dung lượng: Tối thiểu 2GB RAM, 5GB dung lượng trống cho môi trường ảo và cơ sở dữ liệu Chroma.

**Cài đặt**
1. Giải nén và vào thư mục
unzip chatbot-hcmue.zip
cd chatbot-hcmue

2. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate

3. Cài đặt thư viện
pip install -r requirements.txt

4. Cấu hình file .env
Tạo file .env trong thư mục gốc với nội dung sau:
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=models/gemini-2.5-pro
OCR_LANGUAGE=vie


GEMINI_API_KEY: Lấy từ Google Cloud Console (https://cloud.google.com).
MODEL_NAME: Tên model Gemini, mặc định là models/gemini-2.5-pro.
OCR_LANGUAGE: Ngôn ngữ cho OCR (mặc định: vie cho tiếng Việt, thay bằng eng cho tiếng Anh nếu cần).

Lưu ý: Không chia sẻ file .env hoặc API key công khai.
5. Chuẩn bị tài liệu PDF

Copy các file PDF cần xử lý vào thư mục pdf_documents/.
Đảm bảo thư mục này có quyền ghi.

6. Chạy ứng dụng
Trên Windows:
run_chatbot.bat

Hoặc trực tiếp:
python app.py


Mở trình duyệt và truy cập http://localhost:5000 để sử dụng chatbot.

**Xử lý lỗi**

Lỗi "GEMINI_API_KEY không được tìm thấy": Kiểm tra file .env và đảm bảo key hợp lệ.
Lỗi xử lý PDF: Xem log trong processing.log hoặc query.log để biết chi tiết.
Lỗi cài đặt thư viện: Chạy lại pip install -r requirements.txt hoặc kiểm tra kết nối mạng.
Lỗi Tesseract/Poppler: Cài đặt Tesseract và Poppler đúng cách, đảm bảo chúng được thêm vào PATH hệ thống.
Lỗi truy cập localhost: Kiểm tra xem cổng 5000 có đang được sử dụng bởi ứng dụng khác không.

**Cấu trúc thư mục**

pdf_documents/: Thư mục chứa file PDF đầu vào.
db/: Cơ sở dữ liệu Chroma lưu trữ embeddings.
processed_files.json: Lưu metadata của các file PDF đã xử lý.
processing.log: Log xử lý PDF.
query.log: Log truy vấn người dùng.
templates/messenger_chat.html: Giao diện web của chatbot.
.env: File cấu hình (không đẩy lên repository).
app.py: Ứng dụng Flask chính.
rag_engine.py: Lớp xử lý truy vấn RAG.
pdf_processor_adaptive.py: Lớp xử lý PDF và tạo embeddings.
requirements.txt: Danh sách thư viện cần cài đặt.
run_chatbot.bat: Script chạy ứng dụng trên Windows.

**Ghi chú**

Đảm bảo thư mục pdf_documents/ và db/ có quyền ghi.
Hệ thống hỗ trợ lịch sử trò chuyện (tối đa 10 lượt).
Để kiểm tra code, chạy unit test bằng lệnh:python -m unittest test_pdf_processor.py


Không sử dụng ứng dụng ở chế độ debug trong môi trường production. Sử dụng WSGI server như Gunicorn để triển khai thực tế.

Liên hệ
Nếu gặp vấn đề hoặc cần hỗ trợ, liên hệ qua email