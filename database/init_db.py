# database/init_db.py

import os
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Talhao, Clima, Manejo, NDVI

# Carrega as variáveis do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria a conexão com o banco
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Cria todas as tabelas definidas nos models
Base.metadata.create_all(engine)
print("✅ Tabelas criadas com sucesso!")

# ── Dados simulados de uma fazenda ──────────────────────────────

# Criando talhões
t1 = Talhao(nome="Talhão Norte A", area_hectares=45.5,
            cultura="Soja", latitude=-12.5, longitude=-45.2)
t2 = Talhao(nome="Talhão Sul B", area_hectares=30.0,
            cultura="Milho", latitude=-12.8, longitude=-45.5)

session.add_all([t1, t2])
session.commit()
print("✅ Talhões criados!")

# Criando registros climáticos
climas = [
    Clima(talhao_id=t1.id, data=date(2024, 6, 1),
          temperatura_max=34.0, temperatura_min=22.0,
          precipitacao_mm=0.0, umidade_relativa=45.0),
    Clima(talhao_id=t1.id, data=date(2024, 6, 2),
          temperatura_max=36.5, temperatura_min=23.5,
          precipitacao_mm=0.0, umidade_relativa=38.0),
    Clima(talhao_id=t2.id, data=date(2024, 6, 1),
          temperatura_max=33.0, temperatura_min=21.0,
          precipitacao_mm=12.5, umidade_relativa=72.0),
]
session.add_all(climas)

# Criando histórico de manejo
manejos = [
    Manejo(talhao_id=t1.id, data=date(2024, 5, 10),
           tipo="Plantio", descricao="Plantio de soja variedade M8349",
           produto="Semente M8349"),
    Manejo(talhao_id=t2.id, data=date(2024, 5, 12),
           tipo="Pulverização", descricao="Aplicação de herbicida pré-emergente",
           produto="Glifosato 2L/ha"),
]
session.add_all(manejos)

# Criando registros NDVI
ndvis = [
    NDVI(talhao_id=t1.id, data=date(2024, 6, 1),
         valor=0.45, fonte="Sentinel-2"),
    NDVI(talhao_id=t1.id, data=date(2024, 6, 2),
         valor=0.38, fonte="Sentinel-2"),  # Caindo = sinal de estresse!
    NDVI(talhao_id=t2.id, data=date(2024, 6, 1),
         valor=0.72, fonte="Sentinel-2"),  # Saudável
]
session.add_all(ndvis)

session.commit()
print("✅ Dados de exemplo inseridos com sucesso!")
print("\n🌾 Banco de dados Zana AI pronto!")