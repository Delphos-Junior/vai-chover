# Vai Chover? - NASA Space Apps Challenge 2025

## Overview
"Vai Chover?" is a web application developed for the NASA Space Apps Challenge 2025, addressing the "Will It Rain on My Parade?" challenge. It predicts adverse weather conditions (too hot, too cold, too humid, too windy, too rainy, or too uncomfortable) for a specific location and time, using NASA's GPM IMERG data for precipitation, OpenWeatherMap for forecasts, and a DHT22 sensor on a Raspberry Pi for local measurements. The app features an interactive map (Leaflet.js), probability charts (Chart.js), and customizable alerts.

## Features
- **Custom Queries**: Input a city and specific date/time to check weather conditions.
- **Adverse Condition Probabilities**: Calculates probabilities for adverse conditions using a normal distribution model.
- **NASA Data Integration**: Uses GPM IMERG for precipitation data (note: currently uses fallback due to API limitations).
- **Interactive Map**: Displays the city's location with a precipitation-based colored marker.
- **Local Sensor**: Integrates real-time temperature and humidity from a DHT22 sensor.

## Installation
```bash
git clone https://github.com/Delphos-Junior/vai-chover
cd vai-chover
python -m venv venv_rpi
source venv_rpi/bin/activate
pip install -r requirements.txt
python app.py

Access at http://127.0.0.1:5000.

NASA Data Usage
The app integrates NASA's GPM IMERG Early Run dataset for near-real-time precipitation data, accessed via Earthdata's OPeNDAP with a provided token. Due to limitations in accessing future data, a fallback value (0.0 mm/h) is used when API calls fail.
Impact
"Vai Chover?" helps users plan outdoor events by providing personalized weather alerts based on NASA data, enhancing safety and decision-making.
Team
RainGuardians, developed by [Delfino Junior].

Visão Geral (Português)
"Vai Chover?" é um aplicativo web para o NASA Space Apps Challenge 2025, desenvolvido para o desafio "Will It Rain on My Parade?". Ele prevê condições climáticas adversas (muito quente, fria, úmida, ventosa, chuvosa, desconfortável) para um local e horário específicos, usando dados do GPM IMERG da NASA, OpenWeatherMap, e um sensor DHT22 no Raspberry Pi. Inclui mapa interativo (Leaflet.js), gráficos de probabilidade (Chart.js) e alertas personalizados.
Funcionalidades

Consultas Personalizadas: Insira uma cidade e data/hora para verificar condições climáticas.
Probabilidades de Condições Adversas: Calcula probabilidades usando um modelo de distribuição normal.
Integração de Dados NASA: Usa GPM IMERG para dados de precipitação (nota: usa valor fallback devido a limitações da API).
Mapa Interativo: Mostra a localização da cidade com marcador colorido baseado na precipitação.
Sensor Local: Integra temperatura e umidade em tempo real do DHT22.

git clone https://github.com/Delphos-Junior/vai-chover
cd vai-chover
python -m venv venv_rpi
source venv_rpi/bin/activate
pip install -r requirements.txt
python app.py

Acesse em http://127.0.0.1:5000.
Uso de Dados NASA
O app integra o dataset GPM IMERG Early Run da NASA para dados de precipitação em tempo quase real, acessado via OPeNDAP do Earthdata com um token fornecido. Devido a limitações no acesso a datas futuras, usa um valor fallback (0.0 mm/h) quando as chamadas falham.
Impacto
"Vai Chover?" ajuda usuários a planejar eventos ao ar livre com alertas personalizados baseados em dados da NASA, promovendo segurança e decisões informadas.
Equipe
RainGuardians, desenvolvido por [Delfino Junior].


