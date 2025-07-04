import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import openai
import os
from dotenv import load_dotenv
load_dotenv()

class QAEngine:
    def __init__(self, json_path, threshold=0.75):
        self.data = self.load_data(json_path)
        self.questions = [item["question"] for item in self.data]
        self.answers = [item["answer"] for item in self.data]
        self.levels = [item.get("level", "").lower() for item in self.data]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.questions, convert_to_tensor=True)
        self.threshold = threshold

    def load_data(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_answer(self, user_question, level=None):
        user_embedding = self.model.encode(user_question, convert_to_tensor=True)

        # lọc theo level nếu có
        mask = [True] * len(self.questions)
        if level:
            level = level.lower()
            mask = [lvl == level or lvl == "cả hai" for lvl in self.levels]

        filtered_questions = [q for q, m in zip(self.questions, mask) if m]
        filtered_answers = [a for a, m in zip(self.answers, mask) if m]
        filtered_embeddings = self.embeddings[[i for i, m in enumerate(mask) if m]]

        if len(filtered_embeddings) == 0:
            return self.ask_gpt(user_question, level)


        cosine_scores = util.cos_sim(user_embedding, filtered_embeddings)[0]
        top_idx = int(np.argmax(cosine_scores))
        top_score = float(cosine_scores[top_idx])

        if top_score >= self.threshold:
            return filtered_answers[top_idx]
        else:
            return self.ask_gpt(user_question, level)

    def ask_gpt(self, question, level=None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "❌ Không có API KEY GPT (OpenAI)."

        openai.api_key = api_key
        try:
            prompt = "Bạn là trợ lý ảo hỗ trợ sinh viên Trường Đại học Sư phạm TP.HCM. "
            if level:
                prompt += f"Hãy trả lời cho hệ {level}. "
            prompt += f"Câu hỏi: {question}"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Trả lời bằng tiếng Việt, ngắn gọn, chính xác."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Lỗi gọi GPT: {e}"
