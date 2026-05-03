import json
from pathlib import Path

from scraper import scrape_kayak
from storage_json import save_flights

ROUTES_PATH = Path("routes.json")


def load_routes():
    with open(ROUTES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


routes = load_routes()

for route in routes:
    origin = route["origin"]
    destination = route["destination"]
    departure_date = route["departure_date"]
    return_date = route["return_date"]

    print(f"Scraping {origin} → {destination} from {departure_date} to {return_date}")

    result = scrape_kayak(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
    )

    offers = result["offers"]

    for offer in offers:
        offer["origin"] = origin
        offer["destination"] = destination
        offer["departure_date"] = departure_date
        offer["return_date"] = return_date
        offer["source"] = "kayak"

    save_flights(offers)

    print(f"Saved {len(offers)} offers")