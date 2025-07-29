# 注意需要注册 天气访问 账号
import os

import click
import requests
from typing import Optional


@click.command()
@click.argument("location")
@click.option("--unit", default="celsius", help="Temperature unit (celsius/fahrenheit)")
def cli(location: str, unit: str) -> None:
    """A simple weather CLI tool."""
    weather = get_weather(location)
    if weather:
        click.echo(f"Conditions: {weather}")
    else:
        click.echo("Failed to fetch weather data")


def get_weather(location: str) -> Optional[dict]:
    """Fetch weather data from OpenWeatherMap API."""
    try:
        base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        gaode_key = os.getenv("GAODE_DITU")
        gaode_key = "cab8318392aca0607e8a64f67b12ef30" # 临时使用
        params = {
            "key": gaode_key,
            "city": location,
            "extensions": "all",
            "output": "JSON",
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    cli()
