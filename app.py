from flask import Flask, request, jsonify
from qa_engine import QAEngine
import os

app = Flask(__name__)

# Đảm bảo đường dẫn đúng đến file JSON chứa Q&A
DATA_PATH = os.path.join('data', 'qa_1000_cong_tac_sinh_vien_hcmue.json')
qa_engine = QAEngine(DATA_PATH)

# Route mặc định, tránh lỗi 404
@app.route('/')
def index():
    return '''
        ✅ Chatbot HCMUE is running!<br>
        Gửi câu hỏi bằng POST đến endpoint <code>/chat</code> với nội dung JSON:<br>
        <pre>
        {
            "question": "Câu hỏi của bạn"
        }
        </pre>
    '''

# Endpoint để hỏi và nhận câu trả lời
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('question', '')
        if not question:
            return jsonify({'error': 'Bạn cần cung cấp câu hỏi'}), 400

        answer = qa_engine.get_answer(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
