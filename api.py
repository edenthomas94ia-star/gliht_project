from fastapi import FastAPI
from database import init_db, get_offers
from scraper import scrape_kayak

app = FastAPI()
init_db()


@app.get("/")
def home():
    return {"message": "Flight scraper API is running"}


@app.get("/scrape")
def scrape(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str
):
    return scrape_kayak(origin, destination, departure_date, return_date)


@app.get("/offers")
def offers():
    data = get_offers()

    return [
        {
            "origin": x.origin,
            "destination": x.destination,
            "departure_date": x.departure_date,
            "return_date": x.return_date,
            "price": x.price,
            "currency": x.currency,
            "airline": x.airline,
            "duration": x.duration,
            "stops": x.stops,
            "departure_time": x.departure_time,
            "arrival_time": x.arrival_time,
            "source": x.source,
            "collected_at": x.collected_at,
        }
        for x in data
    ]