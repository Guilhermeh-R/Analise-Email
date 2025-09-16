import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Carrega o .env

HF_TOKEN = os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

CLASSIFIER_URL = "https://api-inference.huggingface.co/models/Guilhermeh-r/modelo_classificador"

def query_hf(api_url, payload):
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": f"HF API error: {response.status_code}, {response.text}"}
    return response.json()

# Teste
texto = "Este é um email de teste"
print("Enviando para HF API...")
print(HF_TOKEN)
result = query_hf(CLASSIFIER_URL, {"inputs": texto})
print(result)