# backend/routes/clima.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Cookie
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Talhao, Propriedade
from backend.auth.auth_handler import verificar_token
from backend.services.clima_service import buscar_clima_atual, buscar_previsao_5dias

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

router = APIRouter(prefix="/api", tags=["clima"])

def get_usuario_id(token: str) -> int:
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return int(payload["sub"])

@router.get("/talhoes/{talhao_id}/clima")
def clima_talhao(talhao_id: int, zana_token: str = Cookie(None)):
    """Retorna o clima atual do talhão baseado na sua geolocalização"""
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        talhao = session.query(Talhao).join(Propriedade).filter(
            Talhao.id == talhao_id,
            Propriedade.usuario_id == uid
        ).first()

        if not talhao:
            raise HTTPException(status_code=404, detail="Talhão não encontrado")

        if not talhao.latitude or not talhao.longitude:
            raise HTTPException(
                status_code=400,
                detail="Talhão sem geolocalização cadastrada"
            )

        clima = buscar_clima_atual(talhao.latitude, talhao.longitude)
        previsao = buscar_previsao_5dias(talhao.latitude, talhao.longitude)

        return {
            "talhao": talhao.nome,
            "cultura": talhao.cultura,
            "clima_atual": clima,
            "previsao_5dias": previsao
        }
    finally:
        session.close()

@router.get("/propriedades/{prop_id}/clima-geral")
def clima_propriedade(prop_id: int, zana_token: str = Cookie(None)):
    """Retorna o clima atual da propriedade"""
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = session.query(Propriedade).filter(
            Propriedade.id == prop_id,
            Propriedade.usuario_id == uid
        ).first()

        if not prop:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")

        if not prop.latitude or not prop.longitude:
            raise HTTPException(
                status_code=400,
                detail="Propriedade sem geolocalização cadastrada"
            )

        clima = buscar_clima_atual(prop.latitude, prop.longitude)
        previsao = buscar_previsao_5dias(prop.latitude, prop.longitude)

        return {
            "propriedade": prop.nome,
            "clima_atual": clima,
            "previsao_5dias": previsao
        }
    finally:
        session.close()