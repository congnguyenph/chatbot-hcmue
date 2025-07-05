import os
from dotenv import load_dotenv
from pdf_processor_adaptive import PDFProcessor
import requests
import logging

logging.basicConfig(
    filename="processing.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class RAGEngine:
    def __init__(self):
        load_dotenv()
        self.processor = PDFProcessor()
        #self.processor.process_pdfs()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("MODEL_NAME", "models/gemini-2.5-pro")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY không được tìm thấy trong .env")

    def get_answer(self, question, chat_history=None):
        if not question or len(question.strip()) < 3:
            logging.error("Câu hỏi không hợp lệ hoặc quá ngắn")
            return "❌ Vui lòng nhập câu hỏi hợp lệ (ít nhất 3 ký tự)."

        try:
            results = self.processor.search_similar(question)[:1]
            context = "\n".join([doc.page_content[:800] for doc in results])

            # Ghi log truy vấn
            logging.info(f"Truy vấn: {question}")
            logging.info(f"Ngữ cảnh: {context[:200]}...")  # Ghi log 200 ký tự đầu của ngữ cảnh

            if len(context.strip()) < 20:
                logging.warning(f"Không tìm thấy ngữ cảnh phù hợp cho câu hỏi: {question}")
                return self._ask_llm(question)

            # Tích hợp chat history nếu có
            history_context = ""
            if chat_history:
                history_context = "\nLịch sử trò chuyện:\n" + "\n".join(
                    [f"Q: {q}\nA: {a}" for q, a in chat_history[-3:]]  # Giới hạn 3 lượt trước
                )

            prompt = f"""
Bạn là trợ lý ảo của Trường Đại học Sư phạm TP.HCM, có nhiệm vụ hỗ trợ sinh viên giải đáp các thắc mắc liên quan đến công tác sinh viên, học phí, học bổng, rèn luyện, chính sách và quy định nhà trường.

{history_context}

Dưới đây là phần ngữ cảnh được trích từ tài liệu chính thức của nhà trường:

{context}

Câu hỏi của sinh viên: {question}

Yêu cầu khi trả lời:
- Chỉ sử dụng thông tin trong phần ngữ cảnh.
- Nếu không đủ thông tin, hãy trả lời: “Xin lỗi, tôi chưa tìm thấy thông tin chính xác về nội dung này trong tài liệu.”
- Trả lời ngắn gọn, dễ hiểu, văn phong lịch sự và rõ ràng.

Lưu ý: Không suy đoán hay trả lời dựa trên kiến thức bên ngoài.
"""
            return self._ask_llm(prompt)

        except Exception as e:
            logging.error(f"Lỗi xử lý câu hỏi '{question}': {str(e)}")
            return f"❌ Lỗi: {str(e)}"

    def _ask_llm(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    logging.info(f"Đáp án từ Gemini: {answer[:200]}...")
                    return answer
                logging.warning("Không có phản hồi từ Gemini")
                return "❌ Không có phản hồi từ Gemini."
            logging.error(f"API lỗi: {response.status_code} - {response.text}")
            return f"❌ API lỗi: {response.status_code} - {response.text}"
        except Exception as e:
            logging.error(f"API lỗi: {str(e)}")
            return f"❌ API lỗi: {str(e)}"