# backend/main.py

import os
import sys

# Caminho absoluto da pasta backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.dirname(BASE_DIR))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ai_service.agent import perguntar_zana

app = FastAPI(title="Zana AI — Assistente Agronômica")

# Caminho absoluto para a pasta templates
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

class MensagemChat(BaseModel):
    pergunta: str
    historico: list = []

@app.get("/", response_class=HTMLResponse)
async def pagina_chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )

@app.post("/chat")
async def chat(mensagem: MensagemChat):
    try:
        resposta = perguntar_zana(mensagem.pergunta)
        return JSONResponse({
            "resposta": resposta,
            "status": "ok"
        })
    except Exception as e:
        return JSONResponse({
            "resposta": f"Erro ao processar: {str(e)}",
            "status": "erro"
        }, status_code=500)

@app.get("/health")
async def health():
    return {"status": "Zana AI online 🌾"}