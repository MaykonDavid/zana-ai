# database/models.py

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id            = Column(Integer, primary_key=True)
    nome          = Column(String(100), nullable=False)
    email         = Column(String(200), nullable=False, unique=True)
    senha_hash    = Column(String(255), nullable=False)
    criado_em     = Column(Date, default=datetime.date.today)
    ativo         = Column(Integer, default=1)
    propriedades  = relationship("Propriedade", back_populates="usuario",
                                 cascade="all, delete-orphan")

class Propriedade(Base):
    __tablename__ = "propriedades"
    id                  = Column(Integer, primary_key=True)
    usuario_id          = Column(Integer, ForeignKey("usuarios.id"))
    nome                = Column(String(200), nullable=False)
    cidade              = Column(String(100))
    estado              = Column(String(2))
    area_total_hectares = Column(Float)
    latitude            = Column(Float)
    longitude           = Column(Float)
    usuario             = relationship("Usuario", back_populates="propriedades")
    talhoes             = relationship("Talhao", back_populates="propriedade",
                                       cascade="all, delete-orphan")

class Talhao(Base):
    __tablename__ = "talhoes"
    id              = Column(Integer, primary_key=True)
    propriedade_id  = Column(Integer, ForeignKey("propriedades.id"))
    nome            = Column(String(100), nullable=False)
    area_hectares   = Column(Float)
    cultura         = Column(String(100))
    latitude        = Column(Float)
    longitude       = Column(Float)
    data_plantio    = Column(Date, nullable=True)
    dias_ciclo      = Column(Integer, nullable=True)
    propriedade     = relationship("Propriedade", back_populates="talhoes")
    climas          = relationship("Clima",  back_populates="talhao",
                                   cascade="all, delete-orphan")
    manejos         = relationship("Manejo", back_populates="talhao",
                                   cascade="all, delete-orphan")
    ndvis           = relationship("NDVI",   back_populates="talhao",
                                   cascade="all, delete-orphan")

class Clima(Base):
    __tablename__ = "climas"
    id               = Column(Integer, primary_key=True)
    talhao_id        = Column(Integer, ForeignKey("talhoes.id"))
    data             = Column(Date, nullable=False)
    temperatura_max  = Column(Float)
    temperatura_min  = Column(Float)
    precipitacao_mm  = Column(Float)
    umidade_relativa = Column(Float)
    talhao           = relationship("Talhao", back_populates="climas")

class Manejo(Base):
    __tablename__ = "manejos"
    id          = Column(Integer, primary_key=True)
    talhao_id   = Column(Integer, ForeignKey("talhoes.id"))
    data        = Column(Date, nullable=False)
    tipo        = Column(String(100))
    descricao   = Column(Text)
    produto     = Column(String(200))
    dose        = Column(String(100))
    talhao      = relationship("Talhao", back_populates="manejos")

class NDVI(Base):
    __tablename__ = "ndvis"
    id        = Column(Integer, primary_key=True)
    talhao_id = Column(Integer, ForeignKey("talhoes.id"))
    data      = Column(Date, nullable=False)
    valor     = Column(Float)
    fonte     = Column(String(100))
    talhao    = relationship("Talhao", back_populates="ndvis")