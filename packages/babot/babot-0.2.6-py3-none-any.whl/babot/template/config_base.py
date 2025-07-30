from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

class Config:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", 3))  # Reducir creatividad/razonamiento
    OLLAMA_TOP_P = float(os.getenv("OLLAMA_TOP_P", 0.3))  # Filtrar tokens menos relevantes
