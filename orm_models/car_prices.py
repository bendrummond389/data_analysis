from sqlalchemy import Column, String, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from orm_models.base import Base


class CarPriceDataset(Base):
    __tablename__ = "car_price_dataset"

    brand = Column(String, primary_key=True)
    model = Column(String, primary_key=True)
    year = Column(BigInteger)
    engine_size = Column(Float)
    fuel_type = Column(String)
    transmission = Column(String)
    mileage = Column(BigInteger)
    doors = Column(BigInteger)
    owner_count = Column(BigInteger)
    price = Column(BigInteger)
