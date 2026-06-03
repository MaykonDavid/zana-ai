# backend/auth/auth_handler.py

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# ── Configurações de segurança ───────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "zana-ai-chave-secreta-2024-mude-em-producao")
ALGORITHM = "HS256"
EXPIRE_HORAS = 24  # Token expira em 24 horas

# Contexto de criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha: str) -> str:
    """Criptografa a senha antes de salvar no banco"""
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Verifica se a senha digitada bate com o hash salvo"""
    return pwd_context.verify(senha_pura, senha_hash)

def criar_token(dados: dict) -> str:
    """Cria um token JWT com os dados do usuário"""
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(hours=EXPIRE_HORAS)
    dados_copia.update({"exp": expiracao})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict | None:
    """Verifica e decodifica o token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None