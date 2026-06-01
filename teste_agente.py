# teste_agente.py

import sys
import os

# Garante que Python encontra os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_service.agent import perguntar_zana

print("=" * 60)
print("🌾 ZANA AI — Teste do Agente")
print("=" * 60)

perguntas = [
    "Quais talhões temos na fazenda?",
    "Existe algum talhão em risco de seca agora?",
    "Qual a dose recomendada de glifosato para soja?",  # testa o RAG
]

for pergunta in perguntas:
    print(f"\n👨‍🌾 Pergunta: {pergunta}")
    print("-" * 40)
    try:
        resposta = perguntar_zana(pergunta)
        print(f"🤖 Zana:\n{resposta}")
    except Exception as e:
        print(f"❌ Erro ao processar pergunta: {e}")
    print("=" * 60)