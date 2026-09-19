from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --------------------------------------------------
# CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Smart Weather Assistant",
    version="1.0.0"
)

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class WeatherAlertRequest(BaseModel):
    city: str
    temperature_limit: float
    rain_alert: bool = True

# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# --------------------------------------------------
# WEATHER ADVICE / BUSINESS LOGIC
# --------------------------------------------------

def get_weather_advice(
    temperature: float,
    rain: float,
    wind_speed: float
):
    """
    Analyze weather conditions and
    provide a simple recommendation.
    """

    # If rain is happening
    if rain > 0:
        return "Carry an umbrella. It may rain."

    # Very hot weather
    if temperature >= 35:
        return "Very hot weather. Avoid heavy outdoor activity."

    # Very cold weather
    if temperature <= 10:
        return "Cold weather. Wear warm clothes."

    # Strong wind
    if wind_speed >= 30:
        return "Strong wind. Be careful with outdoor activities."

    # Normal weather
    return "Weather looks good for outdoor activities."


def get_forecast_advice(
    max_temperature,
    rain_probability
):

    if rain_probability >= 70:
        return "High chance of rain. Carry an umbrella."

    if max_temperature >= 35:
        return "Very hot day. Avoid heavy outdoor activity."

    if max_temperature <= 10:
        return "Cold day. Wear warm clothes."

    return "Weather looks suitable for normal outdoor activities."





# --------------------------------------------------
# WEATHER ENDPOINT
# --------------------------------------------------

@app.get("/weather")
def get_weather(city: str):

    # ==================================================
    # STEP 1: GET CITY COORDINATES
    # ==================================================

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geocoding_params = {
        "name": city,
        "count": 1
    }

    try:

        # Call Geocoding API
        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        # Raise error if API returns 4xx/5xx
        geo_response.raise_for_status()

        # Convert JSON response to Python dictionary
        geo_data = geo_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out."
        )

    except requests.exceptions.RequestException as e:
        print("GEOCODING ERROR:", repr(e))

        raise HTTPException(
            status_code=503,
            detail=f"Geocoding error: {str(e)}"
        )


    # ==================================================
    # STEP 2: CHECK WHETHER CITY EXISTS
    # ==================================================

    if not geo_data.get("results"):

        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found."
        )


    # Get first matching location
    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]


    # ==================================================
    # STEP 3: CALL WEATHER API
    # ==================================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        )
    }

    try:

        # Call Weather API
        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        # Check HTTP status
        weather_response.raise_for_status()

        # Convert JSON → Python dictionary
        weather_data = weather_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Weather service timed out."
        )

    except requests.exceptions.RequestException as e:
        print("WEATHER ERROR:", repr(e))

        raise HTTPException(
            status_code=503,
            detail=f"Weather error: {str(e)}"
        )

    # ==================================================
    # STEP 4: EXTRACT CURRENT WEATHER
    # ==================================================

    current = weather_data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    feels_like = current["apparent_temperature"]
    rain = current["precipitation"]
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]


    # ==================================================
    # STEP 5: APPLY OUR BUSINESS LOGIC
    # ==================================================

    advice = get_weather_advice(
        temperature,
        rain,
        wind_speed
    )


    # ==================================================
    # STEP 6: RETURN CLEAN API RESPONSE
    # ==================================================

    return {

        "city": location["name"],

        "country": location.get("country"),

        "latitude": latitude,

        "longitude": longitude,

        "temperature": temperature,

        "humidity": humidity,

        "feels_like": feels_like,

        "rain": rain,

        "wind_speed": wind_speed,

        "weather_code": weather_code,

        "advice": advice
    }




@app.get("/forecast")
def get_forecast(city: str):

    # ==================================================
    # STEP 1: FIND CITY COORDINATES
    # ==================================================

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geocoding_params = {
        "name": city,
        "count": 1
    }

    try:

        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out."
        )

    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=503,
            detail="Geocoding service unavailable."
        )


    # ==================================================
    # STEP 2: CHECK CITY
    # ==================================================

    if not geo_data.get("results"):

        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found."
        )


    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]


    # ==================================================
    # STEP 3: CALL FORECAST API
    # ==================================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {

        "latitude": latitude,

        "longitude": longitude,

        # Daily forecast data
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),

        # Number of forecast days
        "forecast_days": 7,

        # Important for correct local dates
        "timezone": "auto"
    }


    try:

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Weather service timed out."
        )

    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=503,
            detail="Weather service unavailable."
        )


    # ==================================================
    # STEP 4: EXTRACT DAILY DATA
    # ==================================================

    daily = weather_data["daily"]

    dates = daily["time"]

    max_temperatures = daily[
        "temperature_2m_max"
    ]

    min_temperatures = daily[
        "temperature_2m_min"
    ]

    rain_probability = daily[
        "precipitation_probability_max"
    ]


    # ==================================================
    # STEP 5: CREATE CLEAN FORECAST
    # ==================================================

    forecast = []

    for i in range(len(dates)):

        forecast.append({

            "date": dates[i],

            "max_temperature": max_temperatures[i],

            "min_temperature": min_temperatures[i],

            "rain_probability": rain_probability[i],

            "advice": get_forecast_advice(
                max_temperatures[i],
                rain_probability[i]
            )
        })


    # ==================================================
    # STEP 6: RETURN RESPONSE
    # ==================================================

    return {

        "city": location["name"],

        "country": location.get("country"),

        "forecast": forecast
    }



@app.post("/weather/alert")
def create_weather_alert(
    request: WeatherAlertRequest
):

    # ==================================================
    # STEP 1: FIND CITY
    # ==================================================

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geocoding_params = {
        "name": request.city,
        "count": 1
    }

    try:

        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out."
        )

    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=503,
            detail="Geocoding service unavailable."
        )


    # ==================================================
    # STEP 2: CHECK CITY
    # ==================================================

    if not geo_data.get("results"):

        raise HTTPException(
            status_code=404,
            detail=f"City '{request.city}' not found."
        )


    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]


    # ==================================================
    # STEP 3: GET CURRENT WEATHER
    # ==================================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "precipitation"
        )
    }


    try:

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="Weather service timed out."
        )

    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=503,
            detail="Weather service unavailable."
        )


    # ==================================================
    # STEP 4: EXTRACT WEATHER
    # ==================================================

    current = weather_data["current"]

    temperature = current["temperature_2m"]

    rain = current["precipitation"]


    # ==================================================
    # STEP 5: CHECK USER CONDITIONS
    # ==================================================

    alerts = []


    # Temperature alert
    if temperature >= request.temperature_limit:

        alerts.append(
            f"Temperature is above {request.temperature_limit}°C."
        )


    # Rain alert
    if request.rain_alert and rain > 0:

        alerts.append(
            "Rain detected. Carry an umbrella."
        )


    # ==================================================
    # STEP 6: TAKE ACTION
    # ==================================================

    if alerts:

        status = "ALERT"

        # Send alert to external webhook
        notification_sent = send_weather_alert(
            location["name"],
            temperature,
            alerts
        )

        if notification_sent:

            action = (
                "Weather alert triggered "
                "and external notification sent."
            )

        else:

            action = (
                "Weather alert triggered, "
                "but external notification failed."
            )

    else:

        status = "NORMAL"

        notification_sent = False

        action = (
            "No weather alert is triggered."
        )

    # ==================================================
    # STEP 7: RETURN RESULT
    # ==================================================

    return {

        "city": location["name"],

        "temperature": temperature,

        "rain": rain,

        "status": status,

        "alerts": alerts,

        "action": action,

         "notification_sent": notification_sent
    }



def send_weather_alert(
    city: str,
    temperature: float,
    alerts: list
):
    """
    Send an alert to an external webhook.
    """

    payload = {
        "city": city,
        "temperature": temperature,
        "alerts": alerts,
        "message": "Weather alert triggered!"
    }

    try:

        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        return True

    except requests.exceptions.RequestException:

        return False