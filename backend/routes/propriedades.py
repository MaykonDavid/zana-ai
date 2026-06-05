# backend/routes/propriedades.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Cookie
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Propriedade, Talhao
from backend.auth.auth_handler import verificar_token

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

router = APIRouter(prefix="/api", tags=["propriedades"])

# ── Modelos ──────────────────────────────────────────────────────
class PropriedadeIn(BaseModel):
    nome: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    area_total_hectares: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class TalhaoIn(BaseModel):
    nome: str
    area_hectares: Optional[float] = None
    cultura: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_plantio: Optional[str] = None
    dias_ciclo: Optional[int] = None

# ── Helper — pega usuário do token ───────────────────────────────
def get_usuario_id(token: str) -> int:
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return int(payload["sub"])

# ════════════════════════════════════════════════════════════════
#  PROPRIEDADES
# ════════════════════════════════════════════════════════════════

@router.get("/propriedades")
def listar_propriedades(zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        props = session.query(Propriedade)\
            .filter(Propriedade.usuario_id == uid).all()
        return [{"id": p.id, "nome": p.nome, "cidade": p.cidade,
                 "estado": p.estado,
                 "area_total_hectares": p.area_total_hectares,
                 "latitude": p.latitude, "longitude": p.longitude,
                 "total_talhoes": len(p.talhoes)} for p in props]
    finally:
        session.close()

@router.post("/propriedades")
def criar_propriedade(dados: PropriedadeIn, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = Propriedade(usuario_id=uid, **dados.dict())
        session.add(prop)
        session.commit()
        session.refresh(prop)
        return {"id": prop.id, "nome": prop.nome,
                "mensagem": "Propriedade criada com sucesso!"}
    finally:
        session.close()

@router.put("/propriedades/{prop_id}")
def editar_propriedade(prop_id: int, dados: PropriedadeIn,
                       zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = session.query(Propriedade).filter(
            Propriedade.id == prop_id,
            Propriedade.usuario_id == uid
        ).first()
        if not prop:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")
        for k, v in dados.dict().items():
            setattr(prop, k, v)
        session.commit()
        return {"mensagem": "Propriedade atualizada!"}
    finally:
        session.close()

@router.delete("/propriedades/{prop_id}")
def apagar_propriedade(prop_id: int, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = session.query(Propriedade).filter(
            Propriedade.id == prop_id,
            Propriedade.usuario_id == uid
        ).first()
        if not prop:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")
        session.delete(prop)
        session.commit()
        return {"mensagem": "Propriedade apagada!"}
    finally:
        session.close()

# ════════════════════════════════════════════════════════════════
#  TALHÕES
# ════════════════════════════════════════════════════════════════

@router.get("/propriedades/{prop_id}/talhoes")
def listar_talhoes(prop_id: int, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = session.query(Propriedade).filter(
            Propriedade.id == prop_id,
            Propriedade.usuario_id == uid
        ).first()
        if not prop:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")
        return [{"id": t.id, "nome": t.nome, "cultura": t.cultura,
                 "area_hectares": t.area_hectares,
                 "latitude": t.latitude, "longitude": t.longitude,
                 "data_plantio": str(t.data_plantio) if t.data_plantio else None,
                 "dias_ciclo": t.dias_ciclo} for t in prop.talhoes]
    finally:
        session.close()

@router.post("/propriedades/{prop_id}/talhoes")
def criar_talhao(prop_id: int, dados: TalhaoIn,
                 zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        prop = session.query(Propriedade).filter(
            Propriedade.id == prop_id,
            Propriedade.usuario_id == uid
        ).first()
        if not prop:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")

        from datetime import date
        data_plantio = None
        if dados.data_plantio:
            data_plantio = date.fromisoformat(dados.data_plantio)

        talhao = Talhao(
            propriedade_id=prop_id,
            nome=dados.nome,
            area_hectares=dados.area_hectares,
            cultura=dados.cultura,
            latitude=dados.latitude,
            longitude=dados.longitude,
            data_plantio=data_plantio,
            dias_ciclo=dados.dias_ciclo
        )
        session.add(talhao)
        session.commit()
        session.refresh(talhao)
        return {"id": talhao.id, "nome": talhao.nome,
                "mensagem": "Talhão criado com sucesso!"}
    finally:
        session.close()

@router.put("/talhoes/{talhao_id}")
def editar_talhao(talhao_id: int, dados: TalhaoIn,
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

        from datetime import date
        talhao.nome = dados.nome
        talhao.area_hectares = dados.area_hectares
        talhao.cultura = dados.cultura
        talhao.latitude = dados.latitude
        talhao.longitude = dados.longitude
        talhao.dias_ciclo = dados.dias_ciclo
        if dados.data_plantio:
            talhao.data_plantio = date.fromisoformat(dados.data_plantio)
        session.commit()
        return {"mensagem": "Talhão atualizado!"}
    finally:
        session.close()

@router.delete("/talhoes/{talhao_id}")
def apagar_talhao(talhao_id: int, zana_token: str = Cookie(None)):
    uid = get_usuario_id(zana_token)
    session = Session()
    try:
        talhao = session.query(Talhao).join(Propriedade).filter(
            Talhao.id == talhao_id,
            Propriedade.usuario_id == uid
        ).first()
        if not talhao:
            raise HTTPException(status_code=404, detail="Talhão não encontrado")
        session.delete(talhao)
        session.commit()
        return {"mensagem": "Talhão apagado!"}
    finally:
        session.close()