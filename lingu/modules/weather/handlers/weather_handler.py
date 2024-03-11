from datetime import datetime, timedelta
from lingu import cfg, log
import requests
import time

api_key = cfg("weather", "api_key", env_key="OPENWEATHERMAP_API_KEY")

weather_icons = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "⛅",
    "broken clouds": "🌥️",
    "overcast clouds": "☁️",
    "snow": "❄️",
    "sleet": "❄️",
    "freezing": "❄️",
    "tornado": "🌪️",
    "storm": "⛈️",
    "rain": "🌧️",
    "mist": "🌫️",
    "smoke": "🌫️",
    "haze": "🌫️",
    "sand": "🌫️",
    "dust": "🌫️",
    "fog": "🌫️",
    "ash": "🌫️",
    "squalls": "🌫️"
}

wind_categories = [
    (10, 'Calm Breeze'),
    (20, 'Gentle Breeze'),
    (30, 'Light Winds'),
    (40, 'Moderate Winds'),
    (50, 'Fresh Breeze'),
    (60, 'Strong Breeze'),
    (70, 'Near Gale'),
    (80, 'Gale Winds'),
    (90, 'Severe Gale'),
    (100, 'Storm Winds'),
    (110, 'Violent Storm'),
    (120, 'Hurricane Winds'),
    (float('inf'), 'Extreme Hurricane')
]


def wind_speed_to_description(wind_speed: float) -> str:
    """
    Convert a given wind speed to its descriptive category.

    Parameters:
    - wind_speed: The speed of the wind in some consistent unit
      (e.g., km/h or mph)

    Returns:
    A string description of the wind speed.
    """
    for speed, description in wind_categories:
        if wind_speed < speed:
            return description


def find_weather_icon(text):
    text_lower = text.lower()
    for keyword, icon in weather_icons.items():
        if keyword in text_lower:
            return icon
    log.wrn(f"  [weather] no icon found for {text}")
    return "?"


def get_icon_from_weather_data(datapoints):
    for item in datapoints:
        icon = find_weather_icon(item['weather'])
        if icon:
            return icon
    return "?"


def get_text_from_weather_data(datapoints):
    if len(datapoints) > 0:
        weather = datapoints[0]['weather']
        wind = datapoints[0]['wind']
        temp = datapoints[0]['temp']
        return f"{weather}, {wind}, {temp}°C"
    return "?"


def get_info_from_weather_data(datapoints):
    if len(datapoints) > 0:
        temp = datapoints[0]['temp']
        return f"{temp}"
    return "?"


def convert_to_optimized_structure(original_data):
    optimized_data = {
        "column_definitions": {
            "0": "hours_ahead",
            "1": "temperature",
            "2": "weather",
            "3": "wind"
        },
        "data": [],
        "ui_data": []
    }

    current_time_unix = time.time()
    current_time = datetime.utcfromtimestamp(current_time_unix)

    for entry in original_data:
        entry_time_str = entry['time']

        entry_time = datetime.strptime(entry_time_str, "%d.%m.%Y %H")
        entry_time_ui = entry_time.strftime("%d.%m. %H")

        # Calculate the time difference in hours
        time_difference = entry_time - current_time
        hours_ahead = round(time_difference.total_seconds() / 3600)

        temperature = entry['temp']
        weather = entry['weather']
        wind = entry['wind']
        wind_speed = entry['wind_speed']

        optimized_data["data"].append((
            hours_ahead, temperature, weather, wind))
        optimized_data["ui_data"].append((
            f"{entry_time_ui} Uhr",
            f"{temperature}°C",
            f"{find_weather_icon(weather)} {weather}",
            f"{wind} ({wind_speed} km/h)"
        ))

    return optimized_data


def get_weather_data(city: str):
    url = (
        f"http://api.openweathermap.org/data/2.5/forecast?q={city}"
        f"&appid={api_key}&units=metric"
    )

    log.low(f"  [weather] getting weather data for {city}")
    json_weather_data = requests.get(url).json()

    datapoints = []
    if "list" in json_weather_data:
        for item in json_weather_data["list"]:
            item_time = datetime.utcfromtimestamp(item["dt"])
            if item_time <= datetime.utcnow() + timedelta(hours=72):
                temp = int(item['main']['temp'])
                wind_speed = int(item["wind"]["speed"])
                wind = wind_speed_to_description(wind_speed)
                weather = item["weather"][0]["description"]
                datapoints.append({
                    'time': item_time.strftime('%d.%m.%Y %H'),
                    'temp': temp,
                    'weather': weather,
                    'wind': wind,
                    'wind_speed': wind_speed,
                })
            else:
                break

    log.low(f"  [weather] got {len(datapoints)} datapoints")
    for datapoint in datapoints:
        log.low(f"  [weather] {datapoint['time']}: {datapoint['temp']}°C, "
                f"Wetter: {datapoint['weather']}, Wind: {datapoint['wind']}")

    symbol = get_icon_from_weather_data(datapoints)
    text = get_icon_from_weather_data(datapoints)
    info = get_info_from_weather_data(datapoints)

    optimized_stucture = convert_to_optimized_structure(datapoints)
    return optimized_stucture, text, info, symbol
