# rag/indexar_documentos.py

import os
import sys

# Garante que Python encontra os módulos do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documentos")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def carregar_documentos():
    """Percorre todas as subpastas e carrega PDFs e TXTs"""
    documentos = []
    arquivos_carregados = 0
    arquivos_erro = 0

    for raiz, pastas, arquivos in os.walk(DOCS_DIR):
        for arquivo in arquivos:
            caminho = os.path.join(raiz, arquivo)
            
            # Pega o nome da subpasta para identificar a cultura/produto
            subpasta = os.path.relpath(raiz, DOCS_DIR)

            try:
                if arquivo.endswith(".pdf"):
                    loader = PyPDFLoader(caminho)
                    docs = loader.load()
                    # Adiciona metadado de origem em cada trecho
                    for doc in docs:
                        doc.metadata["source"] = arquivo
                        doc.metadata["categoria"] = subpasta
                    documentos.extend(docs)
                    print(f"  ✅ PDF: {subpasta}/{arquivo} ({len(docs)} páginas)")
                    arquivos_carregados += 1

                elif arquivo.endswith(".txt"):
                    loader = TextLoader(caminho, encoding="utf-8")
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source"] = arquivo
                        doc.metadata["categoria"] = subpasta
                    documentos.extend(docs)
                    print(f"  ✅ TXT: {subpasta}/{arquivo}")
                    arquivos_carregados += 1

            except Exception as e:
                print(f"  ❌ Erro ao carregar {arquivo}: {e}")
                arquivos_erro += 1

    print(f"\n📊 Resumo: {arquivos_carregados} carregados, {arquivos_erro} com erro")
    return documentos

def indexar():
    print("=" * 55)
    print("🌾 ZANA AI — Indexador de Documentos Técnicos")
    print("=" * 55)

    print("\n📄 Carregando documentos...\n")
    documentos = carregar_documentos()

    if not documentos:
        print("\n⚠️  Nenhum documento encontrado!")
        print(f"   Coloque PDFs ou TXTs em: {DOCS_DIR}")
        return

    print(f"\n✂️  Dividindo em chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documentos)
    print(f"  ✅ {len(chunks)} chunks criados a partir de {len(documentos)} páginas")

    print(f"\n🔢 Gerando embeddings (pode demorar alguns minutos)...")
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Se já existe um banco, remove para reindexar do zero
    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print(f"  🗑️  Banco anterior removido para reindexação limpa")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(f"\n✅ Indexação concluída com sucesso!")
    print(f"   {len(chunks)} trechos salvos em {CHROMA_DIR}")
    print(f"\n🤖 A Zana AI agora pode consultar esses documentos!")

if __name__ == "__main__":
    indexar()