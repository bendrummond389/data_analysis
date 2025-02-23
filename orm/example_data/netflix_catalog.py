from sqlalchemy import Column, String, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from orm.base import Base


class NetflixDataset(Base):
    __tablename__ = "netflix_dataset"

    show_id = Column(String, primary_key=True)
    type = Column(String)
    title = Column(String)
    director = Column(Text)
    cast = Column(Text)
    country = Column(Text)
    date_added = Column(String)
    release_year = Column(BigInteger)
    rating = Column(String)
    duration = Column(String)
    listed_in = Column(Text)
    description = Column(Text)
    text = Column(Text)
