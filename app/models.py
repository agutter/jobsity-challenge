from .database import Base
from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry

#Defines the Trip class in the ORM.
class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True)
    region = Column(String, nullable=False)
    origin_coord = Column(Geometry('POINT', srid=4326), nullable=False)
    destination_coord = Column(Geometry('POINT', srid=4326), nullable=False)
    datetime = Column(DateTime, nullable=False)
    datasource = Column(String, nullable=False)

