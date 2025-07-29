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
        temp = weather["main"]["temp"]
        if unit == "fahrenheit":
            temp = temp * 9 / 5 + 32
            unit_symbol = "°F"
        else:
            unit_symbol = "°C"

        click.echo(f"Weather in {location}:")
        click.echo(f"Temperature: {temp:.1f}{unit_symbol}")
        click.echo(f"Conditions: {weather['weather'][0]['description']}")
    else:
        click.echo("Failed to fetch weather data")


def get_weather(location: str) -> Optional[dict]:
    """Fetch weather data from OpenWeatherMap API."""
    try:
        # 注意: 实际使用时需要申请自己的API key
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": "your_api_key_here",  # 替换为你的API key
            "units": "metric",
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    cli()
