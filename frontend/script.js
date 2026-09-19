async function getWeather() {

    const city = document.getElementById("city").value;

    const error = document.getElementById("error");

    const card = document.getElementById("weather-card");

    const loading = document.getElementById("loading");


    if (!city) {

        error.innerText = "Please enter a city.";

        return;
    }


    error.innerText = "";

    card.style.display = "none";

    loading.innerText = "Loading weather...";


    try {

        const response = await fetch(
        `/weather?city=${encodeURIComponent(city)}`
    );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Something went wrong"
            );
        }


        document.getElementById("city-name").innerText =
            `${data.city}, ${data.country}`;


        document.getElementById("temperature").innerText =
            data.temperature;


        document.getElementById("humidity").innerText =
            data.humidity;


        document.getElementById("rain").innerText =
            `${data.rain} mm`;


        document.getElementById("wind").innerText =
            `${data.wind_speed} km/h`;


        document.getElementById("advice").innerText =
            data.advice || "Weather information available.";


        card.style.display = "block";


    } catch (err) {

        error.innerText = err.message;

    } finally {

        loading.innerText = "";
    }
}