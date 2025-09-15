from transformers import pipeline
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
from controller import *
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define a PORT
    app.run(host="0.0.0.0", port=port)