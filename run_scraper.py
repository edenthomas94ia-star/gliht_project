from scraper import scrape_kayak
from storage_json import save_flights

result = scrape_kayak(
    origin="PAR",
    destination="TCI",
    departure_date="2026-10-06",
    return_date="2026-10-20"
)

offers = result["offers"]

for offer in offers:
    offer["origin"] = "PAR"
    offer["destination"] = "TCI"
    offer["departure_date"] = "2026-10-06"
    offer["return_date"] = "2026-10-20"
    offer["source"] = "kayak"

save_flights(offers)

print(f"Saved {len(offers)} offers")