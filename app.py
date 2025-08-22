from flask import Flask, render_template, request
import requests
import h5py
import numpy as np
import Adafruit_DHT
import random
import json
from datetime import datetime, date, timedelta
from scipy.stats import norm  # Para distribuição normal

app = Flask(__name__)

# Configurações
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
API_KEY = "a296d2be26d65230eaea338aae41d11a"
EARTHDATA_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Imp1bmlvcl9tZW5kZXMiLCJleHAiOjE3NjEwMDQ3OTksImlhdCI6MTc1NTgxODUwOSwiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5hc2EuZ292IiwiaWRlbnRpdHlfcHJvdmlkZXIiOiJlZGxfb3BzIiwiYWNyIjoiZWRsIiwiYXNzdXJhbmNlX2xldmVsIjozfQ.fgDG1XtqO4U70xWqfh6AkIJGiWQ1fFeeIiDDLmWpzeYv170k75HEZ8m7qOxasXUVqte4CGtjXmYbL7vXGG61CD7yBA8WimEnSowbp5jibTpuG-323j1CKiIiWQUWr3AiA64eHOKelmQXDSRdmTp0iTwVmf470ZmmKKAsuF4S2HSelC19TlVaYJqKgbA3bI5BZwlb7O384GcxVGpSjAKOh0TM3WuN9ZoaYfkdpkflSVmVWmq_TlSMrK5ygpiKJwE1j65lR72JDTXyiWpldYimufHCAyTrXzkX4wCxHZW5AngQvBSI-ClwmC-dk4qrt1uJwoePg-w7yf3MSU8RZPT9Fg"

# Função para calcular o índice de desconforto térmico (THI)
def calculate_thi(temp, humidity):
    return temp - 0.55 * (1 - 0.01 * humidity) * (temp - 14.5)

# Função para calcular probabilidades de condições adversas
def calculate_probabilities(temp, humidity, wind_speed, precip_rate):
    # Dados históricos simulados (média e desvio padrão baseados em clima tropical)
    historical_temps = np.random.normal(26, 4, 200)  # Média 26°C, desvio 4°C
    historical_humidity = np.random.normal(75, 8, 200)  # Média 75%, desvio 8%
    historical_wind = np.random.normal(4, 1.5, 200)  # Média 4 m/s, desvio 1.5 m/s
    historical_precip = np.random.normal(3, 2, 200)  # Média 3 mm/h, desvio 2 mm/h
    
    # Calcular probabilidades usando CDF da distribuição normal
    prob_hot = norm.cdf(temp, loc=35, scale=4) * 100  # Threshold: 35°C
    prob_cold = (1 - norm.cdf(temp, loc=5, scale=4)) * 100  # Threshold: 5°C
    prob_humid = norm.cdf(humidity, loc=80, scale=8) * 100  # Threshold: 80%
    prob_windy = norm.cdf(wind_speed, loc=10, scale=1.5) * 100  # Threshold: 10 m/s
    prob_rain = norm.cdf(precip_rate, loc=10, scale=2) * 100  # Threshold: 10 mm/h
    thi = calculate_thi(temp, humidity)
    prob_uncomfortable = norm.cdf(thi, loc=26, scale=4) * 100  # Threshold: 26
    
    return {
        "hot": min(prob_hot, 100),
        "cold": min(prob_cold, 100),
        "humid": min(prob_humid, 100),
        "windy": min(prob_windy, 100),
        "rain": min(prob_rain, 100),
        "uncomfortable": min(prob_uncomfortable, 100)
    }

# Função para classificar condições climáticas
def classify_weather(temp, humidity, wind_speed, precip_rate):
    conditions = []
    probs = calculate_probabilities(temp, humidity, wind_speed, precip_rate)
    
    if probs["hot"] > 50:
        conditions.append((f"Muito quente ({probs['hot']:.1f}% de probabilidade)", "danger"))
    if probs["cold"] > 50:
        conditions.append((f"Muito fria ({probs['cold']:.1f}% de probabilidade)", "info"))
    if probs["humid"] > 50:
        conditions.append((f"Muito úmida ({probs['humid']:.1f}% de probabilidade)", "warning"))
    if probs["windy"] > 50:
        conditions.append((f"Muito ventosa ({probs['windy']:.1f}% de probabilidade)", "secondary"))
    if probs["rain"] > 50:
        conditions.append((f"Muita chuva ({probs['rain']:.1f}% de probabilidade)", "primary"))
    if probs["uncomfortable"] > 50:
        conditions.append((f"Muito desconfortável ({probs['uncomfortable']:.1f}% de probabilidade)", "dark"))
    
    return conditions if conditions else [("Condições normais (baixa probabilidade de adversidades)", "success")], probs

# Função para obter dados de precipitação do GPM IMERG
def get_gpm_precipitation(lat, lon, date_str):
    try:
        # Usar data atual para IMERG Early Run (não suporta datas futuras)
        current_date = datetime.now().strftime("%Y-%m-%d")
        year = current_date[:4]
        month = current_date[5:7]
        day = current_date[8:10]
        url = f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.06/{year}/{month}/3B-HHR.MS.MRG.3IMERG.{year}{month}{day}-S000000-E002959.0000.V06B.HDF5"
        headers = {"Authorization": f"Bearer {EARTHDATA_TOKEN}"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open("temp_imerg.h5", "wb") as f:
            f.write(response.content)
        
        with h5py.File("temp_imerg.h5", "r") as f:
            precip = f["Grid/precipitationCal"][:]
            lat_grid = f["Grid/lat"][:]
            lon_grid = f["Grid/lon"][:]
            lat_idx = np.argmin(np.abs(lat_grid - lat))
            lon_idx = np.argmin(np.abs(lon_grid - lon))
            precip_rate = float(precip[0, lon_idx, lat_idx])
        
        return precip_rate
    except Exception as e:
        print(f"Erro ao acessar GPM IMERG: {e}")
        return 0.0

# Função para obter dados históricos do GPM IMERG (opcional, para futuro)
def get_gpm_historical_precip(lat, lon, start_date, end_date):
    try:
        url = f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.06/{start_date[:4]}/{start_date[5:7]}/3B-HHR.MS.MRG.3IMERG.{start_date.replace('-', '')}-S000000-E002959.0000.V06B.HDF5"
        headers = {"Authorization": f"Bearer {EARTHDATA_TOKEN}"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open("temp_historical_imerg.h5", "wb") as f:
            f.write(response.content)
        
        with h5py.File("temp_historical_imerg.h5", "r") as f:
            precip = f["Grid/precipitationCal"][:]
            lat_grid = f["Grid/lat"][:]
            lon_grid = f["Grid/lon"][:]
            lat_idx = np.argmin(np.abs(lat_grid - lat))
            lon_idx = np.argmin(np.abs(lon_grid - lon))
            precip_rate = float(precip[0, lon_idx, lat_idx])
        
        return [precip_rate]
    except Exception as e:
        print(f"Erro ao acessar GPM histórico: {e}")
        return [0.0]

@app.route("/", methods=["GET", "POST"])
def index():
    city = "São Paulo"
    sensor_data = {"temperature": None, "humidity": None}
    weather_data = []
    conditions = []
    precip_rate = 0.0
    probs = {"hot": 0, "cold": 0, "humid": 0, "windy": 0, "rain": 0, "uncomfortable": 0}
    lat = 0
    lon = 0

    # Leitura do sensor DHT22
    try:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            sensor_data["temperature"] = round(temperature, 1)
            sensor_data["humidity"] = round(humidity, 1)
        else:
            sensor_data["temperature"] = round(random.uniform(20, 30), 1)
            sensor_data["humidity"] = round(random.uniform(40, 80), 1)
    except:
        sensor_data["temperature"] = round(random.uniform(20, 30), 1)
        sensor_data["humidity"] = round(random.uniform(40, 80), 1)

    # Inicializar selected_datetime
    selected_datetime = None
    if request.method == "POST":
        city = request.form.get("city", "São Paulo").strip()
        selected_datetime = request.form.get("datetime")

    # Definir horário padrão ou selecionado
    selected_dt = datetime.now() + timedelta(hours=3) if not selected_datetime else datetime.fromisoformat(selected_datetime.replace("T", " "))

    # Requisição à API OpenWeatherMap
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        weather_json = response.json()
        weather_data = weather_json.get("list", [])
        lat = weather_json["city"]["coord"]["lat"]
        lon = weather_json["city"]["coord"]["lon"]

        # Extrair dados para o gráfico
        labels = [datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M") for item in weather_data]
        temps = [item["main"]["temp"] for item in weather_data]
        icons = [item["weather"][0]["icon"] for item in weather_data]

        # Filtrar para o horário mais próximo
        if weather_data:
            closest_item = min(weather_data, key=lambda x: abs(datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - selected_dt))
            temp = closest_item["main"]["temp"]
            humidity = closest_item["main"]["humidity"]
            wind_speed = closest_item["wind"]["speed"]
            precip_rate = get_gpm_precipitation(lat, lon, selected_dt.strftime("%Y-%m-%d"))
            conditions, probs = classify_weather(temp, humidity, wind_speed, precip_rate)

    except requests.RequestException:
        weather_data = []
        labels = []
        temps = []
        icons = []
        conditions = [("Erro ao buscar previsão", "danger")]
        probs = {"hot": 0, "cold": 0, "humid": 0, "windy": 0, "rain": 0, "uncomfortable": 0}

    return render_template(
        "index.html",
        city=city,
        sensor_data=sensor_data,
        weather_data={"labels": labels, "temps": temps, "icons": icons},
        conditions=conditions,
        precip_rate=precip_rate,
        probs=probs,
        lat=lat,
        lon=lon
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
