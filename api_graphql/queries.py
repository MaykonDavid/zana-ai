# graphql/queries.py

import strawberry
import sys
import os
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Importa os models do banco e os types do GraphQL
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from database.models import Talhao, Clima, Manejo, NDVI
from api_graphql.graphql_types import TalhaoType, ClimaType, ManejoType, NDVIType

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

@strawberry.type
class Query:

    @strawberry.field
    def talhoes(self) -> List[TalhaoType]:
        """Retorna todos os talhões com seus dados completos"""
        session = get_session()
        talhoes = session.query(Talhao).all()
        resultado = []
        for t in talhoes:
            resultado.append(TalhaoType(
                id=t.id,
                nome=t.nome,
                area_hectares=t.area_hectares,
                cultura=t.cultura,
                latitude=t.latitude,
                longitude=t.longitude,
                climas=[ClimaType(
                    id=c.id, data=c.data,
                    temperatura_max=c.temperatura_max,
                    temperatura_min=c.temperatura_min,
                    precipitacao_mm=c.precipitacao_mm,
                    umidade_relativa=c.umidade_relativa
                ) for c in t.climas],
                manejos=[ManejoType(
                    id=m.id, data=m.data,
                    tipo=m.tipo, descricao=m.descricao,
                    produto=m.produto
                ) for m in t.manejos],
                ndvis=[NDVIType(
                    id=n.id, data=n.data,
                    valor=n.valor, fonte=n.fonte
                ) for n in t.ndvis]
            ))
        session.close()
        return resultado

    @strawberry.field
    def talhao_por_id(self, id: int) -> Optional[TalhaoType]:
        """Busca um talhão específico pelo ID"""
        session = get_session()
        t = session.query(Talhao).filter(Talhao.id == id).first()
        if not t:
            return None
        resultado = TalhaoType(
            id=t.id, nome=t.nome,
            area_hectares=t.area_hectares, cultura=t.cultura,
            latitude=t.latitude, longitude=t.longitude,
            climas=[ClimaType(
                id=c.id, data=c.data,
                temperatura_max=c.temperatura_max,
                temperatura_min=c.temperatura_min,
                precipitacao_mm=c.precipitacao_mm,
                umidade_relativa=c.umidade_relativa
            ) for c in t.climas],
            manejos=[ManejoType(
                id=m.id, data=m.data,
                tipo=m.tipo, descricao=m.descricao,
                produto=m.produto
            ) for m in t.manejos],
            ndvis=[NDVIType(
                id=n.id, data=n.data,
                valor=n.valor, fonte=n.fonte
            ) for n in t.ndvis]
        )
        session.close()
        return resultado

    @strawberry.field
    def alerta_seca(self) -> List[TalhaoType]:
        """
        Retorna talhões em risco de seca:
        - NDVI caindo (último < 0.4)
        - Sem chuva nos últimos 5 dias
        """
        session = get_session()
        talhoes = session.query(Talhao).all()
        em_risco = []

        for t in talhoes:
            # Pega o NDVI mais recente
            ultimo_ndvi = session.query(NDVI)\
                .filter(NDVI.talhao_id == t.id)\
                .order_by(desc(NDVI.data))\
                .first()

            # Pega chuva dos últimos 5 dias
            cinco_dias_atras = date.today() - timedelta(days=5)
            chuva_recente = session.query(Clima)\
                .filter(
                    Clima.talhao_id == t.id,
                    Clima.data >= cinco_dias_atras,
                    Clima.precipitacao_mm > 0
                ).count()

            # Condição de risco: NDVI baixo E sem chuva
            if ultimo_ndvi and ultimo_ndvi.valor < 0.4 and chuva_recente == 0:
                em_risco.append(TalhaoType(
                    id=t.id, nome=t.nome,
                    area_hectares=t.area_hectares, cultura=t.cultura,
                    latitude=t.latitude, longitude=t.longitude,
                    climas=[], manejos=[],
                    ndvis=[NDVIType(
                        id=ultimo_ndvi.id, data=ultimo_ndvi.data,
                        valor=ultimo_ndvi.valor, fonte=ultimo_ndvi.fonte
                    )]
                ))

        session.close()
        return em_risco