import os
import logging
import requests
from dotenv import load_dotenv
from pdf_processor_adaptive import PDFProcessor

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
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("MODEL_NAME", "models/gemini-2.5-pro")
        if not self.api_key:
            raise ValueError("❌ Không tìm thấy GEMINI_API_KEY trong .env")

        if not self.model.startswith("models/"):
            raise ValueError("❌ MODEL_NAME không hợp lệ. Ví dụ hợp lệ: models/gemini-pro")

    def get_answer(self, question, chat_history=None):
        if not question or len(question.strip()) < 3:
            logging.error("Câu hỏi không hợp lệ hoặc quá ngắn")
            return "❌ Vui lòng nhập câu hỏi hợp lệ (ít nhất 3 ký tự)."

        try:
            results = self.processor.search_similar(question)[:1]
            context = "\n".join([doc.page_content[:800] for doc in results])

            logging.info(f"Truy vấn: {question}")
            logging.info(f"Ngữ cảnh: {context[:200]}...")

            if len(context.strip()) < 20:
                logging.warning(f"Không tìm thấy ngữ cảnh phù hợp cho câu hỏi: {question}")
                return self._ask_llm(question)

            history_context = ""
            if chat_history:
                history_context = "\nLịch sử trò chuyện:\n" + "\n".join(
                    [f"Q: {q}\nA: {a}" for q, a in chat_history[-3:]]
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
            return f"❌ Lỗi hệ thống: {str(e)}"

    def _ask_llm(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload
            )
            logging.info(response)
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    logging.info(f"Đáp án từ Gemini: {answer[:200]}...")
                    return answer
                logging.warning("Không có phản hồi từ Gemini.")
                return "❌ Không có phản hồi từ Gemini."

            # Xử lý lỗi API cụ thể hơn
            error_info = response.json().get("error", {}).get("message", "Không rõ lỗi.")
            if response.status_code == 403:
                return "❌ API Key không hợp lệ hoặc bị từ chối truy cập."
            elif response.status_code == 400:
                return f"❌ Lỗi yêu cầu API: {error_info}"
            else:
                logging.error(f"API lỗi: {response.status_code} - {response.text}")
                return f"❌ API lỗi {response.status_code}: {error_info}"

        except Exception as e:
            logging.error(f"API lỗi: {str(e)}")
            return f"❌ Lỗi khi gọi API Gemini: {str(e)}"
