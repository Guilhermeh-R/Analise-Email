from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, GPT2LMHeadModel

# Variáveis globais para carregamento sob demanda
_classifier = None
_generator = None

def get_classifier():
    global _classifier
    if _classifier is None:
        tokenizer = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_classificador")
        model = AutoModelForSequenceClassification.from_pretrained("Guilhermeh-r/modelo_classificador")
        model.eval()
        _classifier = (tokenizer, model)
    return _classifier

def get_generator():
    global _generator
    if _generator is None:
        tokenizer_email = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_geracao")
        model_email = GPT2LMHeadModel.from_pretrained("Guilhermeh-r/modelo_geracao")
        model_email.eval()
        _generator = (tokenizer_email, model_email)
    return _generator

# Função classifica
def _classificar_texto(texto):
    tokenizer, model = get_classifier()
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=200)
    with torch.no_grad():
        outputs = model(**inputs)
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
    tokenizer_email, model_email = get_generator()
    email_en = _traduzir_texto(f'{email} Responda na visão da empresa', source_lang='pt', target_lang='en')
    prompt = f"Question: {email_en}\nResponse:"
    inputs = tokenizer_email.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model_email.generate(
            inputs,
            max_length=200,
            num_return_sequences=1,
            temperature=0.5,
            top_p=0.8,
            repetition_penalty=1.2,
            pad_token_id=tokenizer_email.eos_token_id,
            eos_token_id=tokenizer_email.eos_token_id
        )
    resposta = tokenizer_email.decode(output[0], skip_special_tokens=True)
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