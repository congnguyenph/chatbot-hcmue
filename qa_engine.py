import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import requests
import os

class QAEngine:
    def __init__(self, json_path, threshold=0.7):
        self.data = self.load_data(json_path)
        self.questions = [item["question"] for item in self.data]
        self.answers = [item["answer"] for item in self.data]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.questions, convert_to_tensor=True)
        self.threshold = threshold

    def load_data(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_answer(self, user_question):
        user_embedding = self.model.encode(user_question, convert_to_tensor=True)
        cosine_scores = util.cos_sim(user_embedding, self.embeddings)[0]
        top_score = float(cosine_scores.max())
        top_idx = int(cosine_scores.argmax())

        if top_score >= self.threshold:
            return self.answers[top_idx]
        else:
            return self.ask_deepseek(user_question)

    def ask_deepseek(self, question):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "Không tìm thấy câu trả lời và chưa cấu hình DeepSeek API."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Bạn là trợ lý hỗ trợ sinh viên HCMUE."},
                {"role": "user", "content": question}
            ]
        }
        try:
            res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=body, timeout=15)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Lỗi khi gọi DeepSeek API: {e}"
