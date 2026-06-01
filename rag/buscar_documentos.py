# rag/buscar_documentos.py

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def buscar_em_documentos(pergunta: str, n_resultados: int = 4) -> str:
    """
    Busca nos documentos técnicos os trechos mais relevantes.
    Retorna o contexto formatado com a fonte de cada trecho.
    """
    if not os.path.exists(CHROMA_DIR):
        return "Base de documentos ainda não indexada."

    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    resultados = vectorstore.similarity_search(pergunta, k=n_resultados)

    if not resultados:
        return "Nenhuma informação técnica encontrada para esta pergunta."

    # Formata os resultados com a fonte de cada trecho
    trechos = []
    for doc in resultados:
        fonte = doc.metadata.get("source", "desconhecido")
        categoria = doc.metadata.get("categoria", "")
        trechos.append(f"[Fonte: {fonte} | {categoria}]\n{doc.page_content}")

    return "\n\n---\n\n".join(trechos)