from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DB_URL

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class FlightOffer(Base):
    __tablename__ = "flight_offers"

    id = Column(Integer, primary_key=True, index=True)

    origin = Column(String)
    destination = Column(String)
    departure_date = Column(String)
    return_date = Column(String)

    price = Column(Float)
    currency = Column(String, default="EUR")

    airline = Column(String)
    duration = Column(String)
    stops = Column(String)
    departure_time = Column(String)
    arrival_time = Column(String)

    source = Column(String)
    collected_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_offer(data: dict):
    db = SessionLocal()
    offer = FlightOffer(**data)
    db.add(offer)
    db.commit()
    db.close()


def get_offers():
    db = SessionLocal()
    results = db.query(FlightOffer).order_by(FlightOffer.collected_at.desc()).all()
    db.close()
    return results