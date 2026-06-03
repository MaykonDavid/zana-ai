# backend/auth/auth_routes.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Usuario, Base
from backend.auth.auth_handler import hash_senha, verificar_senha, criar_token, verificar_token

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

router = APIRouter(prefix="/auth", tags=["autenticação"])

# ── Modelos de requisição ────────────────────────────────────────
class CadastroRequest(BaseModel):
    nome: str
    email: str
    senha: str

class LoginRequest(BaseModel):
    email: str
    senha: str

# ── Rota de Cadastro ─────────────────────────────────────────────
@router.post("/cadastro")
async def cadastro(dados: CadastroRequest, response: Response):
    session = Session()

    # Verifica se email já existe
    existente = session.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if existente:
        session.close()
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

    # Cria novo usuário com senha criptografada
    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha)
    )
    session.add(novo_usuario)
    session.commit()

    # Cria token e salva no cookie
    token = criar_token({"sub": str(novo_usuario.id), "email": novo_usuario.email})
    response.set_cookie(
        key="zana_token",
        value=token,
        httponly=True,
        max_age=86400  # 24 horas
    )

    session.close()
    return {
        "mensagem": f"Bem-vindo à Zana AI, {dados.nome}!",
        "usuario": {"id": novo_usuario.id, "nome": dados.nome}
    }

# ── Rota de Login ────────────────────────────────────────────────
@router.post("/login")
async def login(dados: LoginRequest, response: Response):
    session = Session()

    usuario = session.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        session.close()
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    token = criar_token({"sub": str(usuario.id), "email": usuario.email})
    response.set_cookie(
        key="zana_token",
        value=token,
        httponly=True,
        max_age=86400
    )

    session.close()
    return {
        "mensagem": f"Bem-vindo de volta, {usuario.nome}!",
        "usuario": {"id": usuario.id, "nome": usuario.nome}
    }

# ── Rota de Logout ───────────────────────────────────────────────
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("zana_token")
    return {"mensagem": "Logout realizado com sucesso"}

# ── Rota de verificação ──────────────────────────────────────────
@router.get("/me")
async def me(zana_token: str = Cookie(None)):
    if not zana_token:
        raise HTTPException(status_code=401, detail="Não autenticado")

    payload = verificar_token(zana_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {"email": payload.get("email"), "id": payload.get("sub")}