# backend/auth/auth_handler.py

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "zana-ai-chave-secreta-2024")
ALGORITHM = "HS256"
EXPIRE_HORAS = 24

# Força o uso do bcrypt sem verificação de versão
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def hash_senha(senha: str) -> str:
    """Criptografa a senha — limita a 72 chars por segurança"""
    return pwd_context.hash(senha[:72])

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Verifica se a senha bate com o hash"""
    try:
        return pwd_context.verify(senha_pura[:72], senha_hash)
    except Exception:
        return False

def criar_token(dados: dict) -> str:
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(hours=EXPIRE_HORAS)
    dados_copia.update({"exp": expiracao})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None