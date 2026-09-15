#!/usr/bin/env python3

# Import requests so the collector can call the NGINX economics gateway.
import requests

# Import psycopg2 so economic data can be stored in PostgreSQL.
import psycopg2

# Import time so the collector can repeat the collection periodically.
import time

# Import datetime so each collection cycle has a clear timestamp.
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()


# Define the PostgreSQL connection details for the existing operations database.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "ops_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
}


# Request South Africa's GDP data from the existing NGINX World Bank gateway.
URL = (
    "http://localhost:8118/api/economics/v2/country/zaf/"
    "indicator/NY.GDP.MKTP.CD?format=json"
)


def collect_economics():
    # Keep the collector running if the external API temporarily fails.
    try:
        # Request the economic data through our NGINX gateway.
        response = requests.get(URL, timeout=15)

        # Raise an error when the gateway returns an unsuccessful HTTP status.
        response.raise_for_status()

        # Convert the World Bank JSON response into Python data.
        data = response.json()

        # The World Bank response contains metadata followed by the data records.
        records = data[1] if len(data) > 1 else []

        # Stop this cycle if the API returned no economic records.
        if not records:
            print("No economic data returned")
            return

        # Use the newest available GDP record returned by the World Bank.
        record = records[0]

        # Extract the GDP value from the selected record.
        gdp_value = record.get("value")

        # Extract the reporting year from the selected record.
        reporting_year = record.get("date")

        # Do not store an empty GDP value in PostgreSQL.
        if gdp_value is None:
            print("GDP value unavailable")
            return

        # Open a connection to the existing operations PostgreSQL database.
        conn = psycopg2.connect(**DB_CONFIG)

        # Create a cursor so SQL statements can be executed.
        cur = conn.cursor()

        # Create the economics table if it does not already exist.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS economic_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT now(),
                country_code VARCHAR(3) NOT NULL,
                indicator VARCHAR(50) NOT NULL,
                reporting_year INTEGER,
                value NUMERIC
            )
        """)

        # Store the GDP measurement and its original reporting year.
        cur.execute("""
            INSERT INTO economic_data
            (country_code, indicator, reporting_year, value)
            VALUES (%s, %s, %s, %s)
        """, (
            "ZAF",
            "GDP",
            int(reporting_year),
            gdp_value
        ))

        # Permanently save the new economic record.
        conn.commit()

        # Close the database cursor after completing the SQL operation.
        cur.close()

        # Close the database connection and release its resources.
        conn.close()

        # Display the collection timestamp for operational visibility.
        print(f"\n{datetime.now():%Y-%m-%d %H:%M:%S}")

        # Display the country being monitored.
        print("Country: South Africa")

        # Display the World Bank reporting year.
        print(f"Reporting year: {reporting_year}")

        # Display the GDP value returned by the World Bank.
        print(f"GDP: {gdp_value}")

        # Confirm that the measurement was successfully stored.
        print("Economic data stored successfully")

    except Exception as e:
        # Report the error without terminating the continuous collector.
        print(f"Error: {e}")


if __name__ == "__main__":
    # Identify the collector when the process starts.
    print("Starting Economics Collector...")

    # Continue collecting economic data until manually stopped.
    while True:
        # Collect and store the latest available GDP record.
        collect_economics()

        # Wait 60 seconds before checking the gateway again.
        time.sleep(60)
