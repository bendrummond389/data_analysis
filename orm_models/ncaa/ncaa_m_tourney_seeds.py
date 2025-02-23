from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from orm_models.base import Base

class NCAAMTourneySeeds(Base):
    __tablename__ = 'ncaa_m_tourney_seeds'

    id = Column(BigInteger, primary_key=True)
    season = Column(Text)
    seed = Column(Text)
    team_id = Column(BigInteger, ForeignKey('ncaa_m_teams.id'))

    # Relationship to NCAAMTeams
    team = relationship('NCAAMTeams', back_populates='tourney_seeds')

    def __repr__(self):
        return f"<NCAAMTourneySeeds(id={self.id}, season='{self.season}', seed='{self.seed}', team_id={self.team_id})>"