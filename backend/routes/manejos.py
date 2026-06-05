# backend/routes/manejos.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Cookie
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Manejo, Talhao, Propriedade
from backend.auth.auth_handler import verificar_token

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

router = APIRouter(prefix="/api", tags=["manejos"])

class ManejoIn(BaseModel):
    data: str
    tipo: str
    descricao: Optional[str] = None
    produto: Optional[str] = None
    dose: Optional[str] = None

def get_usuario_id(token: str) -> int:
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return int(payload["sub"])

@router.get("/talhoes/{talhao_id}/manejos")
def listar_manejos(talhao_id: int, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        talhao = session.query(Talhao).join(Propriedade).filter(
            Talhao.id == talhao_id,
            Propriedade.usuario_id == uid
        ).first()
        if not talhao:
            raise HTTPException(status_code=404, detail="Talhão não encontrado")
        return [{"id": m.id, "data": str(m.data), "tipo": m.tipo,
                 "descricao": m.descricao, "produto": m.produto,
                 "dose": m.dose} for m in talhao.manejos]
    finally:
        session.close()

@router.post("/talhoes/{talhao_id}/manejos")
def criar_manejo(talhao_id: int, dados: ManejoIn,
                 zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        talhao = session.query(Talhao).join(Propriedade).filter(
            Talhao.id == talhao_id,
            Propriedade.usuario_id == uid
        ).first()
        if not talhao:
            raise HTTPException(status_code=404, detail="Talhão não encontrado")
        manejo = Manejo(
            talhao_id=talhao_id,
            data=date.fromisoformat(dados.data),
            tipo=dados.tipo,
            descricao=dados.descricao,
            produto=dados.produto,
            dose=dados.dose
        )
        session.add(manejo)
        session.commit()
        session.refresh(manejo)
        return {"id": manejo.id, "mensagem": "Manejo registrado!"}
    finally:
        session.close()

@router.delete("/manejos/{manejo_id}")
def apagar_manejo(manejo_id: int, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        manejo = session.query(Manejo).join(Talhao).join(Propriedade).filter(
            Manejo.id == manejo_id,
            Propriedade.usuario_id == uid
        ).first()
        if not manejo:
            raise HTTPException(status_code=404, detail="Manejo não encontrado")
        session.delete(manejo)
        session.commit()
        return {"mensagem": "Manejo apagado!"}
    finally:
        session.close()