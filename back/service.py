from PyPDF2 import PdfReader
from transformers import pipeline
from deep_translator import GoogleTranslator
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification, GPT2LMHeadModel
import torch
from transformers import GPT2LMHeadModel


# Modelo classificador direto do HF
tokenizer = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_classificador")
model = AutoModelForSequenceClassification.from_pretrained("Guilhermeh-r/modelo_classificador")
model.eval()  # modo avaliação

# Modelo de geração de texto direto do HF
tokenizer_email = AutoTokenizer.from_pretrained("Guilhermeh-r/modelo_geracao")
model_email = GPT2LMHeadModel.from_pretrained("Guilhermeh-r/modelo_geracao")
model_email.eval()

#classificar = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = ["Produtivo", "Improdutivo"]

#Gera o texto com mlvoca
def gerarTexto(email: str) -> str:
    # Traduz apenas o conteúdo do email para inglês
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
    
    # Pega só o texto depois de "\nResponse:"
    if "\nResponse:" in resposta:
        resposta = resposta.split("\nResponse:")[-1].strip()

    # Traduz de volta para português
    resposta_pt = _traduzir_texto(resposta, source_lang='en', target_lang='pt')

    return resposta_pt if resposta_pt else "Não consegui gerar uma resposta adequada."

# Analisar PDF e retornar texto e classificação
def analyze_pdf(file):
    text = _process_file(file)
    if not text:
        return {"error": "Failed to extract text from PDF"}, 500
    labels, score = _classificar_texto(text)
    response = gerarTexto(text)

    return { "label": labels, "score": float(score), "suggested": response}

# Analisar texto e retornar classificação
def analyze_text(text):
    labels, score = _classificar_texto(text)
    response = gerarTexto(text)
    return {"label": labels, "score": float(score), "suggested": response}

# Funções auxiliares privadas

#transforma o pdf em texto
def _process_file(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

#traduz o texto de um idioma para outro
def _traduzir_texto(texto, source_lang='pt', target_lang='en'):
    return GoogleTranslator(source=source_lang, target=target_lang).translate(texto)

#função classifica
def _classificar_texto(texto):
    # Tokenizar
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=200)
    
    # Inferência
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()

    # Mapear índice para label
    label = "Produtivo" if pred == 0 else "Improdutivo"
    score = probs[0][pred].item()
    return label, score