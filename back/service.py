from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, GPT2LMHeadModel
import os
from dotenv import load_dotenv

load_dotenv()
# Carregar variável de ambiente
HF_TOKEN = os.getenv("HF_TOKEN")

# Variáveis globais para carregamento sob demanda
_classifier = None
_generator = None

tokenizer_class = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_classificador", token=HF_TOKEN)
model_class = AutoModelForSequenceClassification.from_pretrained("Guilhermeh-r/modelo_classificador", token=HF_TOKEN)

tokenizer_gen = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_gerador", token=HF_TOKEN)
model_gen = GPT2LMHeadModel.from_pretrained("Guilhermeh-r/modelo_gerador", token=HF_TOKEN)


# Função classifica
def _classificar_texto(texto):
    inputs = tokenizer_class(texto, return_tensors="pt", truncation=True, padding=True, max_length=200)
    with torch.no_grad():
        outputs = model_class(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()
    label = "Produtivo" if pred == 0 else "Improdutivo"
    score = probs[0][pred].item()
    return label, score

# Função traduz texto
def _traduzir_texto(texto, source_lang='pt', target_lang='en'):
    return GoogleTranslator(source=source_lang, target=target_lang).translate(texto)

# Função gera texto
def gerarTexto(email: str) -> str:
    email_en = _traduzir_texto(f'{email} Responda na visão da empresa', source_lang='pt', target_lang='en')
    prompt = f"Question: {email_en}\nResponse:"
    
    inputs = tokenizer_gen(prompt, return_tensors="pt")
    
    with torch.no_grad():
        output = model_gen.generate(
            **inputs,
            max_length=200,
            num_return_sequences=1,
            temperature=0.5,
            top_p=0.8,
            repetition_penalty=1.2,
            pad_token_id=tokenizer_gen.eos_token_id,
            eos_token_id=tokenizer_gen.eos_token_id
        )
    
    resposta = tokenizer_gen.decode(output[0], skip_special_tokens=True)
    
    if "\nResponse:" in resposta:
        resposta = resposta.split("\nResponse:")[-1].strip()
    
    resposta_pt = _traduzir_texto(resposta, source_lang='en', target_lang='pt')
    return resposta_pt if resposta_pt else "Não consegui gerar uma resposta adequada."

# Função processa PDF
def _process_file(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
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