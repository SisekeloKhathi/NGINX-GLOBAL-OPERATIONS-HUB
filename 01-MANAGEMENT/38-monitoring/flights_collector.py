#!/usr/bin/env python3

# Import requests so the collector can call the NGINX flight-data gateway.
import requests

# Import psycopg2 so flight data can be stored in PostgreSQL.
import psycopg2

# Import time so the collector can repeat the collection every minute.
import time

# Import datetime so each collection cycle has a timestamp in the terminal.
from datetime import datetime


# Define the PostgreSQL connection details for the existing operations database.
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ops_db",
    "user": "admin",
    "password": "secret"
}


# Use the existing NGINX gateway rather than connecting directly to OpenSky.
URL = "http://localhost:8118/api/flights/api/states/all"


def collect_flights():
    # Keep each collection cycle running even if the external API temporarily fails.
    try:
        # Request the current aircraft state data through NGINX.
        response = requests.get(URL, timeout=15)

        # If the gateway is serving a cached 429, back off politely.
        # This aligns with the gateway's own 429 cache window (15 minutes).
        if response.status_code == 429:
            print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S}")
            print("Rate limited by OpenSky - backing off 15 minutes")
            time.sleep(900)
            return

        # Raise an error if the gateway returns an unsuccessful HTTP status.
        response.raise_for_status()

        # Convert the OpenSky JSON response into a Python dictionary.
        data = response.json()

        # Open a connection to the existing operations PostgreSQL database.
        conn = psycopg2.connect(**DB_CONFIG)

        # Create a cursor for executing SQL statements.
        cur = conn.cursor()

        # Create the flight-state table if it does not already exist.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flight_states (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT now(),
                aircraft_count INTEGER NOT NULL
            )
        """)

        # OpenSky stores aircraft state vectors in the "states" array.
        states = data.get("states") or []

        # Count the aircraft returned by the API for this collection cycle.
        aircraft_count = len(states)

        # Store the current aircraft count in PostgreSQL.
        cur.execute("""
            INSERT INTO flight_states (aircraft_count)
            VALUES (%s)
        """, (aircraft_count,))

        # Commit the transaction so the measurement is permanently stored.
        conn.commit()

        # Close the cursor after completing the database operation.
        cur.close()

        # Close the database connection and release its resources.
        conn.close()

        # Display the collection timestamp for operational visibility.
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S}")

        # Display the number of aircraft currently returned by OpenSky.
        print(f"Aircraft detected: {aircraft_count}")

        # Confirm that the measurement was successfully stored.
        print("Flight data stored successfully")

    except Exception as e:
        # Report errors without terminating the continuous collector.
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Starting Flight Collector...")
    while True:
        collect_flights()
        time.sleep(60)
