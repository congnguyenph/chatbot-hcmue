import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class QAEngine:
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.qa_pairs = json.load(f)
        self.questions = [item['question'] for item in self.qa_pairs]
        self.answers = [item['answer'] for item in self.qa_pairs]
        self.vectorizer = TfidfVectorizer().fit(self.questions)
        self.question_vecs = self.vectorizer.transform(self.questions)

    def get_answer(self, question):
        vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(vec, self.question_vecs)
        best_match_idx = similarities.argmax()
        return self.answers[best_match_idx]
