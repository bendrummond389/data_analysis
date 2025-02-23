from sqlalchemy import Column, BigInteger, Float, ForeignKey
from ..base import Base


class MortalityRate2014(Base):
    __tablename__ = "mortality_rate_2014"

    id = Column(BigInteger, primary_key=True)
    fips_code = Column(BigInteger, ForeignKey("fips.fips_code"))
    mortality_rate_2014_min = Column(Float)
    mortality_rate_2014_max = Column(Float)
