from transformers import pipeline
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
from controller import *
from flask_cors import CORS
import requests
import asyncio

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)