import logging

class Config:
    logging_level = logging.DEBUG

    url = '127.0.0.1'
    port = 8050

    parameters_map = {
    'temperature': ['Температура', '°C'],
    'relative_humidity': ['Относительная влажность', '%'],
    'precipitation_probability': ['Вероятность осадков', '%'],
    'surface_pressure': ['Давление', 'hPa'],
    'visibility': ['Видимость', 'м'],
    'wind_speed': ['Скорость ветра', 'км/ч'],
}