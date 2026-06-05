# backend/main.py

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))

from fastapi import FastAPI, Request, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.auth.auth_routes import router as auth_router
from backend.auth.auth_handler import verificar_token
from ai_service.agent import perguntar_zana

app = FastAPI(title="Zana AI — Assistente Agronômica")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

# Registra as rotas de autenticação
app.include_router(auth_router)

from backend.routes.propriedades import router as prop_router
from backend.routes.manejos import router as manejo_router

app.include_router(prop_router)
app.include_router(manejo_router)

class MensagemChat(BaseModel):
    pergunta: str

# ── Página de Login/Cadastro ─────────────────────────────────────
@app.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

# ── Página principal — exige login ──────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def pagina_chat(request: Request, zana_token: str = Cookie(None)):
    # Se não tiver token, redireciona para login
    if not zana_token:
        return RedirectResponse(url="/login")

    payload = verificar_token(zana_token)
    if not payload:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={"usuario_email": payload.get("email")}
    )

# ── Rota da Fazenda ─────────────────────────────────────────────────
@app.get("/fazenda", response_class=HTMLResponse)
async def pagina_fazenda(request: Request, zana_token: str = Cookie(None)):
    if not zana_token or not verificar_token(zana_token):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request, name="fazenda.html"
    )

# ── Rota do chat ─────────────────────────────────────────────────
@app.post("/chat")
async def chat(mensagem: MensagemChat, zana_token: str = Cookie(None)):
    if not zana_token or not verificar_token(zana_token):
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)
    try:
        resposta = perguntar_zana(mensagem.pergunta)
        return JSONResponse({"resposta": resposta, "status": "ok"})
    except Exception as e:
        return JSONResponse({"resposta": f"Erro: {str(e)}", "status": "erro"}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "Zana AI online 🌾"}