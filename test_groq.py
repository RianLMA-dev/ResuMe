import os
from dotenv import load_dotenv
from groq import Groq

# Força o carregamento do arquivo .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("1. Testando leitura da chave no .env:")
if not api_key:
    print("   ❌ GROQ_API_KEY NÃO FOI ENCONTRADA NO .ENV!")
else:
    print(f"   ✅ Chave encontrada: {api_key[:8]}...{api_key[-4:]}")

print("\n2. Consultando modelos disponíveis na sua conta Groq...")
try:
    client = Groq(api_key=api_key)
    models = client.models.list()
    available_models = [m.id for m in models.data]
    
    print("   ✅ Conexão bem-sucedida! Modelos disponíveis para você:")
    for model in available_models:
        print(f"      - {model}")
        
except Exception as e:
    print("   ❌ Erro de autenticação/conexão com a Groq:")
    print(f"      {e}")