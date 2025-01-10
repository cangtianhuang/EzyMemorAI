import time

from flask import render_template, request, jsonify

from core.ezymemorAI import EzyMemorAI


class ChatInterface:
    def __init__(self):
        self.ai = None

    def initialize_ai(self, target_dir, vector_store_path):
        if target_dir and vector_store_path:
            self.ai = EzyMemorAI(target_dir, vector_store_path)

    def handle_query(self, question):
        if not self.ai:
            return "AI not initialized"
        return self.ai.search(question)

    def render(self):
        if request.method == 'POST':
            target_dir = request.form.get('target_dir')
            vector_store_path = request.form.get('vector_store_path')
            if target_dir and vector_store_path:
                try:
                    self.initialize_ai(target_dir, vector_store_path)
                    return jsonify({"success": True, "message": "AI初始化成功"})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 400

            question = request.form.get('question')
            if question:
                try:
                    # answer = self.handle_query(question)
                    time.sleep(1)
                    answer = "This is an AI response."
                    return jsonify({"success": True, "answer": answer})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 400

        return render_template('index.html')

    def reset(self):
        self.ai = None
        return jsonify({"success": True, "message": "重置成功"})
