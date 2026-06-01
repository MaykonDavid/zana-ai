import requests
import os
import sys
from langchain_core.tools import tool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from rag.buscar_documentos import buscar_em_documentos

# Endereço do nosso servidor GraphQL local
# Mantenha na porta 8001 onde sua api_graphql está rodando
GRAPHQL_URL = "http://localhost:8001/graphql"

def executar_query(query: str) -> dict:
    """Função auxiliar que executa qualquer query GraphQL no servidor local"""
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=10  # Evita que o agente trave se o servidor cair
        )
        return response.json()
    except Exception as e:
        return {"error": f"Não foi possível conectar à API GraphQL: {str(e)}"}

# ── As Tools que o agente Gemini pode usar ─────────────────────────────

@tool
def buscar_todos_talhoes(dummy: str = "") -> str:
    """
    Busca todos os talhões da fazenda com seus dados de clima,
    manejo e NDVI. Use quando precisar de uma visão geral da fazenda
    ou comparar todos os talhões.
    """
    query = """
    query {
      talhoes {
        nome
        cultura
        ndvis {
          data
          valor
        }
        climas {
          data
          precipitacaoMm
          temperaturaMax
        }
      }
    }
    """
    resultado = executar_query(query)
    return str(resultado)

@tool
def buscar_alertas_seca(dummy: str = "") -> str:
    """
    Verifica quais talhões estão em risco de seca agora.
    Use quando o usuário perguntar sobre risco de seca,
    estresse hídrico ou talhões que precisam de irrigação.
    """
    query = """
    query {
      alertaSeca {
        nome
        cultura
        ndvis {
          data
          valor
        }
      }
    }
    """
    resultado = exec_query = executar_query(query)
    return str(resultado)

@tool
def buscar_talhao_por_id(talhao_id: str) -> str:
    """
    Busca dados detalhados de um talhão específico pelo ID.
    Use quando o usuário mencionar um talhão específico pelo número
    ou quando precisar de detalhes de um talhão em particular.
    Parâmetro: o ID numérico do talhão como string (ex: '1', '2')
    """
    query = f"""
    query {{
      talhaoPorId(id: {talhao_id}) {{
        nome
        cultura
        ndvis {{
          data
          valor
        }}
        climas {{
          data
          precipitacaoMm
          temperaturaMax
        }}
      }}
    }}
    """
    resultado = executar_query(query)
    return str(resultado)

@tool
def consultar_documentos_tecnicos(pergunta: str) -> str:
    """
    Consulta manuais técnicos e bulas de agroquímicos para responder
    perguntas sobre: doses de produtos, manejo de pragas e doenças,
    recomendações agronômicas, épocas de plantio, adubação,
    sintomas de deficiências, e informações técnicas das culturas
    de soja, milho, manga, maracujá, café, tomate e cebola.
    Use sempre que a pergunta envolver recomendações técnicas
    que não estão nos dados do banco.
    """
    return buscar_em_documentos(pergunta)