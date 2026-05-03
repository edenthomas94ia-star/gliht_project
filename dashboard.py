import streamlit as st
import pandas as pd
from storage_json import load_flights

st.title("Flight Price Intelligence System")

data = load_flights()

if not data:
    st.info("No flight data yet.")
else:
    df = pd.DataFrame(data)

    st.subheader("Collected flight offers")
    df = df.sort_values("price")
    st.dataframe(df)

    st.subheader("Best offer")
    best = df.iloc[0]
    st.metric("Best price", f"{best['price']} €")

    st.write({
        "airline": best.get("airline"),
        "duration": best.get("duration"),
        "stops": best.get("stops"),
        "departure_time": best.get("departure_time"),
        "arrival_time": best.get("arrival_time"),
        "collected_at": best.get("collected_at"),
    })

    st.subheader("Price history")
    df["collected_at"] = pd.to_datetime(df["collected_at"])
    st.line_chart(df.sort_values("collected_at"), x="collected_at", y="price")