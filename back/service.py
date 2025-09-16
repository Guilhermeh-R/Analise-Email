import os
import requests
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")  # export HF_TOKEN=seu_token
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

CLASSIFIER_URL = "https://api-inference.huggingface.co/models/Guilhermeh-r/modelo_classificador"
GENERATOR_URL = "https://api-inference.huggingface.co/models/Guilhermeh-r/modelo_gerador"

# Chama Hugging Face API
def query_hf(api_url, payload):
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": f"HF API error: {response.text}"}
    return response.json()

# Classificar texto
def _classificar_texto(texto):
    result = query_hf(CLASSIFIER_URL, {"inputs": texto})
    if "error" in result:
        return "Erro", 0.0
    # Dependendo do modelo, pode vir como lista de dicionários [{"label":"LABEL_0", "score":0.98}]
    label = result[0][0]["label"]
    score = result[0][0]["score"]
    return ("Produtivo" if label == "LABEL_0" else "Improdutivo", score)

# Traduz texto (mantém sua função)
def _traduzir_texto(texto, source_lang='pt', target_lang='en'):
    return GoogleTranslator(source=source_lang, target=target_lang).translate(texto)

# Geração de resposta
def gerarTexto(email: str):
    email_en = _traduzir_texto(f'{email} Responda na visão da empresa', 'pt', 'en')
    result = query_hf(GENERATOR_URL, {"inputs": email_en, "parameters": {"max_length": 200}})
    if "error" in result:
        return "Não consegui gerar uma resposta adequada."

    resposta = result[0]["generated_text"]
    resposta_pt = _traduzir_texto(resposta, 'en', 'pt')
    return resposta_pt

# Extrair texto PDF
def _process_file(file):
    reader = PdfReader(file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

# Analisar texto
def analyze_text(text):
    label, score = _classificar_texto(text)
    suggested = gerarTexto(text)
    return {"label": label, "score": float(score), "suggested": suggested}

# Analisar PDF
def analyze_pdf(file):
    text = _process_file(file)
    if not text:
        return {"error": "Failed to extract text from PDF"}, 500
    label, score = _classificar_texto(text)
    suggested = gerarTexto(text)
    return {"label": label, "score": float(score), "suggested": suggested}