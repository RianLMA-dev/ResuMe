from app.agents.extractor import extract_application
from app.schemas import EmailInput

EMAIL = """
Olá! Recebemos sua candidatura para a vaga de Engenheiro de IA Júnior na Acme Tech.
Seu perfil foi selecionado para a próxima etapa: um teste técnico em Python e FastAPI.
Você tem até sexta-feira para enviar a solução pelo link https://acme.com/teste?token=abc123.
Dúvidas: recrutamento@acme.com
Requisitos da vaga: Python, FastAPI, SQL, noções de LLMs.
"""

resultado = extract_application(EmailInput(raw_text=EMAIL))
print(resultado.model_dump_json(indent=2))