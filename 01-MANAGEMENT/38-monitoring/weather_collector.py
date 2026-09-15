#!/usr/bin/env python3

# Import requests so the collector can call the NGINX weather gateway.
import requests

# Import psycopg2 so the collector can write weather data into PostgreSQL.
import psycopg2

# Import time so the collector can wait between collection cycles.
import time

# Import datetime so each collection cycle can be clearly logged.
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()


# Define the PostgreSQL connection details used by the collector.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "ops_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
}


# Use the existing NGINX public data gateway instead of calling Open-Meteo directly.
URL = (
    "http://localhost:8118/api/weather/v1/forecast"
    "?latitude=-26.2041"
    "&longitude=28.0473"
    "&current_weather=true"
)


def collect_weather():
    # Start the collection operation and handle failures without stopping the collector.
    try:
        # Request the current weather data through our NGINX gateway.
        response = requests.get(URL, timeout=10)

        # Stop processing if the gateway returns an HTTP error.
        response.raise_for_status()

        # Convert the JSON response into a Python data structure.
        data = response.json()

        # Extract the current weather section from the API response.
        weather = data["current_weather"]

        # Open a connection to the existing operations database.
        conn = psycopg2.connect(**DB_CONFIG)

        # Create a cursor so SQL commands can be executed.
        cur = conn.cursor()

        # Create the weather table if it does not already exist.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT now(),
                temperature NUMERIC,
                windspeed NUMERIC,
                winddirection NUMERIC,
                weathercode INTEGER
            )
        """)

        # Store the current weather measurement in PostgreSQL.
        cur.execute("""
            INSERT INTO weather_data
            (temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s)
        """, (
            weather["temperature"],
            weather["windspeed"],
            weather["winddirection"],
            weather["weathercode"]
        ))

        # Permanently save the new weather record.
        conn.commit()

        # Close the database cursor after the SQL work is complete.
        cur.close()

        # Close the PostgreSQL connection so resources are released.
        conn.close()

        # Display the collection timestamp for operational visibility.
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S}")

        # Display the current temperature returned by the weather API.
        print(f"Temperature: {weather['temperature']} °C")

        # Display the current wind speed returned by the weather API.
        print(f"Wind speed: {weather['windspeed']} km/h")

        # Display the current wind direction returned by the weather API.
        print(f"Wind direction: {weather['winddirection']}°")

        # Display the weather condition code returned by the API.
        print(f"Weather code: {weather['weathercode']}")

        # Confirm that the database write completed successfully.
        print("Weather data stored successfully")

    except Exception as e:
        # Report the error while keeping the collector available for the next cycle.
        print(f"Error: {e}")


if __name__ == "__main__":
    # Identify the collector when the program starts.
    print("Starting Weather Collector...")

    # Continue collecting weather data until the process is stopped manually.
    while True:
        # Collect and store the latest weather measurement.
        collect_weather()

        # Wait 60 seconds before collecting the next measurement.
        time.sleep(60)
