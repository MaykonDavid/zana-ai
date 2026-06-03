from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# Tabela de dados do cliente/produtor/técnico
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(Date, default=datetime.date.today)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo

    # Relacionamento — cada usuário terá suas próprias propriedades
    propriedades = relationship("Propriedade", back_populates="usuario")

# Tabela de dados da propriedade
class Propriedade(Base):
    __tablename__ = "propriedades"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome = Column(String(200), nullable=False)
    cidade = Column(String(100))
    estado = Column(String(2))
    area_total_hectares = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)

    usuario = relationship("Usuario", back_populates="propriedades")
    talhoes = relationship("Talhao", back_populates="propriedade")

# Tabela de Talhões (parcelas da fazenda)
class Talhao(Base):
    __tablename__ = "talhoes"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)  # Ex: "Talhão Norte A"
    area_hectares = Column(Float)               # Tamanho em hectares
    cultura = Column(String(100))               # Ex: "Soja", "Milho"
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relacionamentos com outras tabelas
    climas = relationship("Clima", back_populates="talhao")
    manejos = relationship("Manejo", back_populates="talhao")
    ndvis = relationship("NDVI", back_populates="talhao")
    propriedade_id = Column(Integer, ForeignKey("propriedades.id"))
    propriedade = relationship("Propriedade", back_populates="talhoes")

# Tabela de registros climáticos
class Clima(Base):
    __tablename__ = "climas"
    
    id = Column(Integer, primary_key=True)
    talhao_id = Column(Integer, ForeignKey("talhoes.id"))  # Liga ao talhão
    data = Column(Date, nullable=False)
    temperatura_max = Column(Float)  # °C
    temperatura_min = Column(Float)  # °C
    precipitacao_mm = Column(Float)  # Chuva em milímetros
    umidade_relativa = Column(Float) # %
    
    talhao = relationship("Talhao", back_populates="climas")

# Tabela de histórico de manejo
class Manejo(Base):
    __tablename__ = "manejos"
    
    id = Column(Integer, primary_key=True)
    talhao_id = Column(Integer, ForeignKey("talhoes.id"))  # Liga ao talhão
    data = Column(Date, nullable=False)
    tipo = Column(String(100))        # Ex: "Plantio", "Pulverização", "Colheita"
    descricao = Column(Text)          # Detalhes da operação
    produto = Column(String(200))     # Produto usado (se houver)
    
    talhao = relationship("Talhao", back_populates="manejos")

# Tabela de índice NDVI (saúde da vegetação)
class NDVI(Base):
    __tablename__ = "ndvis"
    
    id = Column(Integer, primary_key=True)
    talhao_id = Column(Integer, ForeignKey("talhoes.id"))  # Liga ao talhão
    data = Column(Date, nullable=False)
    valor = Column(Float)             # Entre -1 e 1 (quanto mais próximo de 1, mais saudável)
    fonte = Column(String(100))        # Ex: "Sentinel-2", "Landsat"
    
    talhao = relationship("Talhao", back_populates="ndvis")