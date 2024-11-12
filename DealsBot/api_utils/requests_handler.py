import requests
from dotenv import load_dotenv
import os

load_dotenv()


def fetch_offers(query, zip_code, limit=100, offset=0):
    # Define the base URL and headers

    url = os.getenv("API_SERVICE_URL")
    headers = {
        "x-clientkey": os.getenv("X_CLIENTKEY"),
        "x-apikey": os.getenv("X_APIKEY")
    }

    # Set up the query parameters
    params = {
        "as": "web",
        "limit": limit,
        "offset": offset,
        "q": query,
        "zipCode": zip_code
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    # Check for successful response
    if response.status_code == 200:
        return response.json()  # Return JSON response if successful
    else:
        response.raise_for_status()  # Raise an error for unsuccessful responses
