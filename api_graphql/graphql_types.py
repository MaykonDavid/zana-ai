# graphql/types.py

import strawberry
from typing import List, Optional
from datetime import date

@strawberry.type
class ClimaType:
    id: int
    data: date
    temperatura_max: float
    temperatura_min: float
    precipitacao_mm: float
    umidade_relativa: float

@strawberry.type
class ManejoType:
    id: int
    data: date
    tipo: str
    descricao: str
    produto: Optional[str]  # Optional = pode ser nulo

@strawberry.type
class NDVIType:
    id: int
    data: date
    valor: float
    fonte: str

@strawberry.type
class TalhaoType:
    id: int
    nome: str
    area_hectares: float
    cultura: str
    latitude: float
    longitude: float
    climas: List[ClimaType]    # Lista de registros climáticos
    manejos: List[ManejoType]  # Lista de manejos
    ndvis: List[NDVIType]      # Lista de NDVIs