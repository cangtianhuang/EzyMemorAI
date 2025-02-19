from socket import SocketIO

from flask import Flask, request, jsonify

from core.knowledge_base.document_db import DocumentDB
from core.knowledge_base.vector_db import VectorDB
from services.file_service import FileService
from services.rag_service import RagService

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize services
vector_db = VectorDB()
document_db = DocumentDB()
file_service = FileService(vector_db=vector_db, document_db=document_db)
rag_service = RagService(vector_db=vector_db)

# Chat API
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = rag_service.generate_response(message)
    return jsonify({"reply": response})

# File Sorting API
@app.route('/api/file-sorting/preview', methods=['POST'])
def preview_files():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400

    structure = file_service.show_directory_tree(path)
    return jsonify({
        "Structure": structure
    })

@app.route('/api/file-sorting/organize', methods=['POST'])
def organize_files():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400

    deep_understanding = data.get('deepUnderstanding', False)
    old_structure, new_structure, classify_out= file_service.organize_directory_tree(path, deep_understanding)
    return jsonify({
        "oldStructure": old_structure,
        "newStructure": new_structure,
        "classifyOut": classify_out
    })

@app.route('/api/file-sorting/apply', methods=['POST'])
def apply_sort():
    data = request.json
    path = data.get('path')
    classify_out = data.get('classifyOut')
    if not path or not classify_out:
        return jsonify({"error": "Path and classification data is required"}), 400

    success = file_service.apply_directory_tree(path, classify_out)
    return jsonify({"success": success})

# Monitoring API
@app.route('/api/monitoring/paths', methods=['GET'])
def get_monitored_paths():
    paths = file_service.get_monitored_paths()
    return jsonify({"paths": paths})

@app.route('/api/monitoring/paths', methods=['POST'])
def add_monitored_path():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400

    success = file_service.add_monitored_path(path)
    return jsonify({"success": success})

@app.route('/api/monitoring/paths', methods=['DELETE'])
def remove_monitored_path():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"error": "Path is required"}), 400

    success = file_service.remove_monitored_path(path)
    return jsonify({"success": success})

# Settings API
@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = {"snapshot_dir": "./core/file_management/.snapshots",
                "vector_db_dir": "./core/knowledge_base/.vector",
                "document_db_path": "./core/knowledge_base/docs.db"}
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
