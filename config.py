"""
Configuration module for Haqdarshak AI Scheme Knowledge Extraction System.
Loads environment variables and sets system-wide defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Database
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "haqdarshak.db"))

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()  # 'mock', 'gemini', 'openai'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash" if LLM_PROVIDER == "gemini" else "mock-extraction-model-v1")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
PROMPT_VERSION = "v1.2.0-grounded"

# Token Pricing (USD per 1M tokens) - Source: Google Cloud Gemini 2.5 Flash pricing Oct 2026
INPUT_TOKEN_PRICE_PER_M = float(os.getenv("INPUT_TOKEN_PRICE_PER_M", "0.075"))
OUTPUT_TOKEN_PRICE_PER_M = float(os.getenv("OUTPUT_TOKEN_PRICE_PER_M", "0.30"))

# OCR Configuration
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
OCR_PRIMARY_LANGS = "eng+hin"
OCR_MIN_TEXT_CHARS = int(os.getenv("OCR_MIN_TEXT_CHARS", "40"))

# Storage Directories
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"
SYNTHETIC_DATA_DIR = BASE_DIR / "synthetic_data"
OUTPUTS_DIR = BASE_DIR / "outputs"

for directory in [SAMPLE_DOCS_DIR, SYNTHETIC_DATA_DIR, OUTPUTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
