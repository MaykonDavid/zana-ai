# backend/auth/auth_routes.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
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

class CadastroRequest(BaseModel):
    nome: str
    email: str
    senha: str

class LoginRequest(BaseModel):
    email: str
    senha: str

@router.post("/cadastro")
async def cadastro(dados: CadastroRequest, response: Response):
    # ── Validações ───────────────────────────────────────────────
    if len(dados.nome.strip()) < 2:
        raise HTTPException(status_code=400, detail="Nome muito curto")

    if "@" not in dados.email:
        raise HTTPException(status_code=400, detail="Email inválido")

    if len(dados.senha) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 6 caracteres")

    if len(dados.senha) > 72:
        raise HTTPException(status_code=400, detail="Senha deve ter no máximo 72 caracteres")

    session = Session()
    try:
        existente = session.query(Usuario).filter(
            Usuario.email == dados.email.lower().strip()
        ).first()

        if existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        novo_usuario = Usuario(
            nome=dados.nome.strip(),
            email=dados.email.lower().strip(),
            senha_hash=hash_senha(dados.senha)
        )
        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

        token = criar_token({
            "sub": str(novo_usuario.id),
            "email": novo_usuario.email,
            "nome": novo_usuario.nome
        })

        response.set_cookie(
            key="zana_token",
            value=token,
            httponly=True,
            max_age=86400
        )

        return {
            "mensagem": f"Bem-vindo à Zana AI, {novo_usuario.nome}!",
            "usuario": {"id": novo_usuario.id, "nome": novo_usuario.nome}
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        session.close()

@router.post("/login")
async def login(dados: LoginRequest, response: Response):
    session = Session()
    try:
        usuario = session.query(Usuario).filter(
            Usuario.email == dados.email.lower().strip()
        ).first()

        if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")

        token = criar_token({
            "sub": str(usuario.id),
            "email": usuario.email,
            "nome": usuario.nome
        })

        response.set_cookie(
            key="zana_token",
            value=token,
            httponly=True,
            max_age=86400
        )

        return {
            "mensagem": f"Bem-vindo de volta, {usuario.nome}!",
            "usuario": {"id": usuario.id, "nome": usuario.nome}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        session.close()

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("zana_token")
    return {"mensagem": "Logout realizado com sucesso"}

@router.get("/me")
async def me(zana_token: str = Cookie(None)):
    if not zana_token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = verificar_token(zana_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return {
        "email": payload.get("email"),
        "nome": payload.get("nome"),
        "id": payload.get("sub")
    }