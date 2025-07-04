
import json
import os
import traceback
from datetime import datetime

import numpy as np
import httpx
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

load_dotenv()

class QAEngine:
    def __init__(self, json_path, threshold=0.85, model="deepseek/deepseek-r1:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Không tìm thấy OPENROUTER_API_KEY trong biến môi trường.")

        self.model_name = model
        self.threshold = threshold
        self.data = self._load_data(json_path)
        self.questions = [item["question"] for item in self.data]
        self.answers = [item["answer"] for item in self.data]
        self.levels = [item.get("level", "").lower() for item in self.data]

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.embedder.encode(self.questions, convert_to_tensor=True)

    def _load_data(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"❌ Lỗi khi đọc file JSON {path}: {e}")

    def _log_interaction(self, question, level, source):
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/conversations.log", "a", encoding="utf-8") as log:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log.write(f"[{timestamp}] [{source}] Level: {level} | Q: {question}\n")
        except Exception:
            pass

    def get_answer(self, user_question, level=None):
        user_embedding = self.embedder.encode(user_question, convert_to_tensor=True)

        mask = [True] * len(self.questions)
        if level:
            level = level.lower()
            mask = [lvl == level or lvl == "cả hai" for lvl in self.levels]

        filtered_qas = [
            (q, a, i) for i, (q, a, m) in enumerate(zip(self.questions, self.answers, mask)) if m
        ]
        if not filtered_qas:
            return self._ask_openrouter(user_question, level)

        filtered_embeddings = self.embeddings[[i for _, _, i in filtered_qas]]
        cosine_scores = util.cos_sim(user_embedding, filtered_embeddings)[0]
        top_idx = int(np.argmax(cosine_scores))
        top_score = float(cosine_scores[top_idx])

        if top_score >= self.threshold:
            question, answer, _ = filtered_qas[top_idx]
            self._log_interaction(user_question, level, "embedding")
            return answer

        self._log_interaction(user_question, level, "openrouter")
        return self._ask_openrouter(user_question, level)

    def _ask_openrouter(self, question, level=None):
        system_prompt = (
            "Bạn là Chatbot về công tác sinh viên của Trường Đại học Sư phạm Thành phố Hồ Chí Minh (HCMUE). "
            "Luôn trả lời BẰNG TIẾNG VIỆT. "
            "Chỉ trả lời đúng trọng tâm trong 1 câu duy nhất, không giải thích, không mở rộng."
        )

        user_prompt = f"Hệ {level}. " if level else ""
        user_prompt += question

        http_client = httpx.Client(proxies=None, timeout=httpx.Timeout(10.0))
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                http_client=http_client
            )
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://your-site.com",
                    "X-Title": "Chatbot HCMUE"
                },
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            traceback.print_exc()
            return f"❌ Lỗi khi gọi OpenRouter: {str(e)}"
        finally:
            http_client.close()
