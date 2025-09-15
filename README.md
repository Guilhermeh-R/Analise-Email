# 📧 AnaliseEmail

Sistema inteligente para análise automática de e-mails e documentos PDF, com classificação de produtividade e sugestão de respostas.

## 🗂 Estrutura do Projeto

```
AnaliseEmail/
├──.venv/
├── back/
│   ├── main.py
│   ├── controller.py
│   ├── service.py
│   └── ...
├── front/
│   └── app/
│       └── src/
│           └── app/
│               ├── page.tsx
│               ├── layout.tsx
│               └── globals.css
│           └── ...
├── README.md
└── .gitignore
```

## 🚀 Como rodar

### Backend (Flask)
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python back/main.py
```

### Frontend (Next.js)
```bash
cd front/app
npm install
npm run dev
```

## ⚡ Funcionalidades

- Upload e análise de PDFs
- Classificação de texto: produtivo ou improdutivo
- Sugestão automática de resposta

## 👨‍💻 Autor

- Guilhermeh-R

---

> Sinta-se livre para contribuir, abrir issues ou sugerir melhorias!
