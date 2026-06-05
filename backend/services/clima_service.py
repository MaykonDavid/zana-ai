# backend/services/clima_service.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def buscar_clima_atual(lat: float, lon: float) -> dict:
    """
    Busca o clima atual para uma coordenada geográfica.
    Retorna temperatura, umidade, chuva e condição do tempo.
    """
    if not API_KEY:
        return {"erro": "Chave OpenWeatherMap não configurada"}

    if not lat or not lon:
        return {"erro": "Coordenadas não informadas"}

    try:
        url = f"{BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",   # Celsius
            "lang": "pt_br"      # Descrições em português
        }

        with httpx.Client(timeout=10) as client:
            res = client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

        return {
            "cidade": data.get("name", "—"),
            "temperatura": data["main"]["temp"],
            "sensacao_termica": data["main"]["feels_like"],
            "temperatura_max": data["main"]["temp_max"],
            "temperatura_min": data["main"]["temp_min"],
            "umidade": data["main"]["humidity"],
            "descricao": data["weather"][0]["description"].capitalize(),
            "vento_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "chuva_mm": data.get("rain", {}).get("1h", 0.0),
            "pressao": data["main"]["pressure"],
            "visibilidade_km": round(data.get("visibility", 0) / 1000, 1),
            "nuvens_percent": data["clouds"]["all"]
        }

    except httpx.TimeoutException:
        return {"erro": "Timeout ao consultar OpenWeatherMap"}
    except Exception as e:
        return {"erro": f"Erro ao buscar clima: {str(e)}"}


def buscar_previsao_5dias(lat: float, lon: float) -> list:
    """
    Busca previsão do tempo para os próximos 5 dias (a cada 3 horas).
    Retorna um resumo por dia.
    """
    if not API_KEY or not lat or not lon:
        return []

    try:
        url = f"{BASE_URL}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "pt_br",
            "cnt": 40  # 5 dias × 8 previsões por dia
        }

        with httpx.Client(timeout=10) as client:
            res = client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

        # Agrupa por dia
        dias = {}
        for item in data["list"]:
            dia = item["dt_txt"][:10]  # Pega só a data YYYY-MM-DD
            if dia not in dias:
                dias[dia] = {
                    "data": dia,
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "chuva_mm": 0.0,
                    "umidade": item["main"]["humidity"],
                    "descricao": item["weather"][0]["description"].capitalize()
                }
            else:
                # Atualiza máximas e mínimas
                dias[dia]["temp_max"] = max(
                    dias[dia]["temp_max"], item["main"]["temp_max"])
                dias[dia]["temp_min"] = min(
                    dias[dia]["temp_min"], item["main"]["temp_min"])
                dias[dia]["chuva_mm"] += item.get("rain", {}).get("3h", 0.0)

        return list(dias.values())[:5]

    except Exception as e:
        return [{"erro": str(e)}]