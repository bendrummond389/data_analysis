
from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from orm_models.base import Base



class NCAAMTeams(Base):
    __tablename__ = 'ncaa_m_teams'

    id = Column(BigInteger, primary_key=True)
    team_name = Column(Text)
    first_d1_season = Column(BigInteger)
    last_d1_season = Column(BigInteger)

    # Relationship to NCAAMTourneySeeds
    tourney_seeds = relationship('NCAAMTourneySeeds', back_populates='team')

    def __repr__(self):
        return f"<NCAAMTeams(id={self.id}, team_name='{self.team_name}', first_d1_season={self.first_d1_season}, last_d1_season={self.last_d1_season})>"