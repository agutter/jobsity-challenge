from datetime import datetime
from typing import List, Union
import uuid
from pydantic import BaseModel, BaseConfig
from shapely.geometry import Point
from shapely import wkt
from psycopg2.extensions import register_adapter, AsIs

"""
Defines the validation schemas for the API endpoints.
"""
#Allow arbitrary types like Point.
BaseConfig.arbitrary_types_allowed = True

def adapt_pydantic_point(point):
    return AsIs(repr(wkt.dumps(point)))

register_adapter(Point, adapt_pydantic_point)

class TripBaseSchema(BaseModel):
    region: str
    origin_coord: str
    destination_coord: str
    datetime: str
    datasource: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class AddTripSchema(TripBaseSchema):
    pass

class AddListTripSchema(BaseModel):
    trips: List[TripBaseSchema]

class TripResponse(TripBaseSchema):
    id: int

class ListTripResponse(BaseModel):
    status: str
    results: int
    trips: List[TripResponse]

class CSVTripResponse(BaseModel):
    status: str
    results: int

class WeeklyAverageTripsResponse(BaseModel):
    status: str
    weekly_average_trips: float

class WeeklyAverageTripsByRegionResponse(WeeklyAverageTripsResponse):
    region: str

class WeeklyAverageTripsByBoundingBoxResponse(WeeklyAverageTripsResponse):
    bottom_left: str
    top_right: str

