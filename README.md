# 🌤️ Smart Weather Assistant

A full-stack weather application built with **FastAPI, Python, JavaScript, and Open-Meteo API**.

The application fetches real-time weather information for any city, applies custom business logic to generate smart weather advice, caches API responses to reduce unnecessary external API calls, and can trigger external webhook notifications for weather alerts.

🔗 **Live Demo:**  
https://smart-weather-assistant-9eep.onrender.com

---

## 🚀 Features

- 🌍 Search weather by city name
- 🌡️ Real-time temperature
- 💧 Humidity information
- 🌡️ Feels-like temperature
- 🌧️ Rain/precipitation information
- 💨 Wind speed
- 🌦️ Weather condition code
- 🧠 Smart weather advice
- ⚡ Response caching
- 🚨 Weather alert system
- 🔔 External webhook notification
- 🛡️ API error handling
- ⏱️ Timeout handling
- 🚦 Rate-limit handling
- 📚 Automatic FastAPI Swagger documentation
- 🎨 Responsive frontend
- ☁️ Deployed on Render
- 🔄 Automatic deployment through GitHub

---

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ HTML/CSS/JS      │
                    │    Frontend      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Cache Check     │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
              Cache Hit              Cache Miss
                 │                       │
                 │                       ▼
                 │              ┌─────────────────┐
                 │              │ Open-Meteo API  │
                 │              └────────┬────────┘
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    ┌──────────────────┐
                    │ Business Logic   │
                    │ Smart Advice      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ JSON Response    │
                    └──────────────────┘
