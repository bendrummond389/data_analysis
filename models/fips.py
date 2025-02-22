from sqlalchemy import Column, BigInteger, String
from .base import Base


class Fips(Base):
    __tablename__ = "fips"

    fips_code = Column(BigInteger, primary_key=True)
    state = Column(String)
    county = Column(String)
