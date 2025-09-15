from flask import Blueprint, Flask, request, jsonify
from PyPDF2 import PdfReader
from service import *

bp = Blueprint('controller', __name__)

@bp.route('/process', methods=['POST'])
def process_pdf():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Não é um arquivo PDF válido'}), 404
    data = analyze_pdf(file)
    if not data:
        return jsonify({'error': 'Falha ao processar PDF'}), 500
    return jsonify(data), 200

@bp.route('/process_Text', methods=['POST'])
def process_text():
    data = request.get_json()

    text = data['text']
    if text.strip() == "":
        return jsonify({'error': 'Empty text provided'}), 400

    return jsonify(analyze_text(text)), 200