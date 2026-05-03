from scraper import scrape_kayak

result = scrape_kayak(
    origin="PAR",
    destination="TCI",
    departure_date="2026-10-06",
    return_date="2026-10-20"
)

print(result)