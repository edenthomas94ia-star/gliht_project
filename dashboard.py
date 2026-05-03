import streamlit as st
import pandas as pd
from database import init_db, get_offers
from scraper import scrape_kayak

init_db()

st.title("Flight Price Intelligence System")

st.sidebar.header("Search")

origin = st.sidebar.text_input("Departure airport/city code", "PAR")
destination = st.sidebar.text_input("Destination airport/city code", "TCI")

departure_date = st.sidebar.date_input("Departure date")
return_date = st.sidebar.date_input("Return date")

if st.sidebar.button("Scrape flights"):
    result = scrape_kayak(
        origin=origin.upper(),
        destination=destination.upper(),
        departure_date=str(departure_date),
        return_date=str(return_date)
    )

    st.success(f"{result['count']} offers collected")
    st.write(result)

data = get_offers()

rows = [
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

df = pd.DataFrame(rows)

if df.empty:
    st.info("No flights collected yet.")
else:
    st.subheader("Collected flight offers")

    df["collected_at"] = pd.to_datetime(df["collected_at"])
    df = df.sort_values("price")

    st.dataframe(df)

    st.subheader("Best offer")
    best = df.iloc[0]

    st.metric("Best price", f"{best['price']} €")

    st.write({
        "airline": best["airline"],
        "duration": best["duration"],
        "stops": best["stops"],
        "departure_time": best["departure_time"],
        "arrival_time": best["arrival_time"],
    })

    st.subheader("Price history")
    history = df.sort_values("collected_at")
    st.line_chart(history, x="collected_at", y="price")