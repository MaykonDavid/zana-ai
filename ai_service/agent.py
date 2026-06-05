# ai_service/agent.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from ai_service.tools import (buscar_todos_talhoes, 
                              buscar_alertas_seca, 
                              buscar_talhao_por_id, 
                              consultar_documentos_tecnicos, 
                              buscar_clima_talhao
)

load_dotenv()

# ── Configurando o Groq ──────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Modelo poderoso e gratuito
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=2048
)

# ── Ferramentas disponíveis ──────────────────────────────────────
tools = [
    buscar_todos_talhoes,
    buscar_alertas_seca,
    buscar_talhao_por_id,
    consultar_documentos_tecnicos,
    buscar_clima_talhao
]

# ── Personalidade da Zana ────────────────────────────────────────
SYSTEM_PROMPT = """Você é a Zana AI, uma assistente agrônomica inteligente 
especializada em agricultura de precisão no Brasil.

Você tem acesso a dados reais da fazenda: talhões, histórico climático 
e índices NDVI (saúde da vegetação).

Suas responsabilidades:
- Analisar riscos de seca, estresse hídrico e anomalias na lavoura.
- Sugerir ações de manejo com base nas variáveis climáticas.
- Identificar talhões que precisam de atenção imediata (ex: NDVI baixo).
- Explicar seus raciocínios de forma clara para o agrônomo.

Sempre que possível:
- Use os dados reais disponíveis via ferramentas.
- Seja objetiva e direta nas recomendações.
- Explique o que os números significam na prática.
- Use unidades brasileiras (hectares, mm, °C).

Você responde sempre em português do Brasil."""

# ── Criando o agente com LangGraph ──────────────────────────────
agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

def perguntar_zana(pergunta: str) -> str:
    """Função principal para interagir com a Zana AI"""
    mensagens = {"messages": [HumanMessage(content=pergunta)]}
    resultado = agent_executor.invoke(mensagens)
    ultima_mensagem = resultado["messages"][-1]
    return ultima_mensagem.content