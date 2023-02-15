from datetime import datetime
from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from sqlalchemy.sql import func, text
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from shapely.geometry import Point
from shapely import wkt, wkb
from typing import List
import geoalchemy2
import csv
import codecs
import io
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import numpy as np

"""
    This file defines the API endpoints for the application.
"""

#Creates the API Router
router = APIRouter()

"""
    POST endpoints to ingest data into the API.
"""

# Adds a single trip to the DB.
"""    
    Due to issues converting and handling Shapely/GeoAlchemy Points, it became necessary
    to process the data both before ingesting and returning it to convert it to the proper
    formats.
    The first post endpoint has a commented line with how it should have worked directly
    if it mapped and converted the datatypes properly.
"""
@router.post('/add', status_code=status.HTTP_201_CREATED, response_model=schemas.TripResponse)
def add_trip(trip: schemas.AddTripSchema, db: Session = Depends(get_db)):
    trip_dict = {
        "region" : trip.region,
        "origin_coord" : wkt.loads(trip.origin_coord),
        "destination_coord" : wkt.loads(trip.destination_coord),
        "datetime" : datetime.strptime(trip.datetime, '%Y-%m-%d %H:%M:%S'),
        "datasource" : trip.datasource
        }
    new_trip = models.Trip(**trip_dict)
    #new_trip = models.Trip(**trip.dict())
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    new_trip_dict = {
        "id" : new_trip.id,
        "region" : new_trip.region,
        "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(new_trip.origin_coord)),
        "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(new_trip.destination_coord)),
        "datetime" : new_trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "datasource" : new_trip.datasource
        }
    return new_trip_dict

# Adds a list of trips to the DB.
"""
    The non existance of a resfresh_all method forces us to make a choice. We could bulk save all the data at once
    with the bulk_save_objects method, however the SQLAlchemy documentation explains that setting the return_defaults
    flag to obtain the generated IDs ends up having worse performance than using add_all, which is equivalent to
    running all the single adds. This last option allows for refreshing the IDs though performance may be sacrificed.
"""
@router.post('/addlist', status_code=status.HTTP_201_CREATED, response_model=schemas.ListTripResponse)
def add_trips(tripList: schemas.AddListTripSchema, db: Session = Depends(get_db)):
    new_trips = []
    for trip in tripList.trips:
        trip_dict = {
            "region" : trip.region,
            "origin_coord" : wkt.loads(trip.origin_coord),
            "destination_coord" : wkt.loads(trip.destination_coord),
            "datetime" : datetime.strptime(trip.datetime, '%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trip = models.Trip(**trip_dict)
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)
        new_trip_dict = {
            "id" : new_trip.id,
            "region" : new_trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(new_trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(new_trip.destination_coord)),
            "datetime" : new_trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : new_trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

# Uploads a CSV with a list of trips which are then added to the DB.
"""
    Unlike the previous method, when batch uploading data we decide not to sacrifice performance
    and use the bulk_save_objects method, since it might not make sense to return a huge list with
    all the added trips for large CSV files. This will be the fastest and most scalable way to ingest
    data.
"""
@router.post('/upload', status_code=status.HTTP_201_CREATED, response_model=schemas.CSVTripResponse) #schemas.ListTripResponse
def upload_trips(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    background_tasks.add_task(file.file.close)
    trips = list(csvReader)
    new_trips = []
    for trip in trips:
        trip_dict = {
            "region" : trip["region"],
            "origin_coord" : wkt.loads(trip["origin_coord"]),
            "destination_coord" : wkt.loads(trip["destination_coord"]),
            "datetime" : datetime.strptime(trip["datetime"], '%Y-%m-%d %H:%M:%S'),
            "datasource" : trip["datasource"]
            }
        new_trip = models.Trip(**trip_dict)
        new_trips.append(new_trip)
        
    db.bulk_save_objects(new_trips)
    db.commit()
    return {'status': 'success', 'results': len(new_trips)}

"""
    GET endpoints to acquire data from the API.
"""

# Returns all existing trips in the DB.
"""
    Because of the Point type mapping issues, we must process the results to return them in a valid format.
"""
@router.get('/', response_model=schemas.ListTripResponse)
def get_trips(db: Session = Depends(get_db)):
    trips = db.query(models.Trip).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips found")
    new_trips = []  #We could use a comprehension list but this feels more readable.
    for trip in trips:
        new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

# Returns a single trip by ID.
@router.get('/{id}', response_model=schemas.TripResponse)
def get_trip(id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trip with this id: {id} found")
    new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
    return new_trip_dict

# Returns all trips for a given region.
@router.get('/region/{region}', response_model=schemas.ListTripResponse)
def get_trips_by_region(region: str, db: Session = Depends(get_db)):
    trips = db.query(models.Trip).filter(models.Trip.region == region).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this region: {region} found")
    new_trips = []  #We could use a comprehension list but this feels more readable.
    for trip in trips:
        new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

# Returns all trips for a given datasource.
@router.get('/datasource/{datasource}', response_model=schemas.ListTripResponse)
def get_trips_by_datasource(datasource: str, db: Session = Depends(get_db)):
    trips = db.query(models.Trip).filter(models.Trip.datasource == datasource).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this datasource: {datasource} found")
    new_trips = []  #We could use a comprehension list but this feels more readable.
    for trip in trips:
        new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

# Returns all trips for a given date (at a day level in format "YYYY-mm-dd").
@router.get('/date/{date}', response_model=schemas.ListTripResponse)
def get_trips_by_date(date: str, db: Session = Depends(get_db)):
    dt = datetime.strptime(date, '%Y-%m-%d')
    trips = db.query(models.Trip).filter(func.date_trunc('day', models.Trip.datetime) == func.date_trunc('day', dt)).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this day: {func.date_trunc('day', date)} found")
    new_trips = []  #We could use a comprehension list but this feels more readable.
    for trip in trips:
        new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

# Returns all trips for a given datetime (at a datetime level in format "YYYY-mm-dd HH:MM:SS").
@router.get('/datetime/{datetime}', response_model=schemas.ListTripResponse)
def get_trips_by_datetime(datetime: datetime, db: Session = Depends(get_db)):
    trips = db.query(models.Trip).filter(models.Trip.datetime == datetime).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this datetime: {datetime} found")
    new_trips = []  #We could use a comprehension list but this feels more readable.
    for trip in trips:
        new_trip_dict = {
            "id" : trip.id,
            "region" : trip.region,
            "origin_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.origin_coord)),
            "destination_coord" : wkt.dumps(geoalchemy2.shape.to_shape(trip.destination_coord)),
            "datetime" : trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "datasource" : trip.datasource
            }
        new_trips.append(new_trip_dict)
    return {'status': 'success', 'results': len(new_trips), 'trips': new_trips}

"""
    GET endpoints to acquire results and visualizations from the API.
"""

# Get Weekly Average Number of Trips for an Area By Region
@router.get('/weekly/{region}', response_model=schemas.WeeklyAverageTripsByRegionResponse)
def get_weekly_average_trips_by_region(region: str, db: Session = Depends(get_db)):
    f = open('Queries/similar_trips_by_region.sql', "r")
    query = f.read().replace("{region}", region)
    f.close()
    weekly_trips = db.execute(text(query)).first()
    if not weekly_trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this region: {region} found")
    return {'status': 'success', 'region': weekly_trips.region, 'weekly_average_trips': weekly_trips.weekly_average}

# Get Weekly Average Number of Trips for an Area By Bounding Box
"""
    Expects the bottom left and top right points of the desired bounding box.
"""
@router.get('/weekly/{bottom_left}/{top_right}', response_model=schemas.WeeklyAverageTripsByBoundingBoxResponse)
def get_weekly_average_trips_by_bbox(bottom_left: str, top_right: str, db: Session = Depends(get_db)):
    f = open('Queries/similar_trips_by_bounding_box.sql', "r")
    query = f.read().replace("{bottom_left}", bottom_left).replace("{top_right}", top_right)
    f.close()
    weekly_trips = db.execute(text(query)).first()
    if not weekly_trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for this bounding box: ({bottom_left}, {top_right}) found")
    return {'status': 'success', 'bottom_left': weekly_trips.bottom_left, 'top_right': weekly_trips.top_right, 'weekly_average_trips': weekly_trips.weekly_average}

# Get the regions where the 'cheap_mobile' datasource has appeared in.
@router.get('/cheap_mobile/', response_model=None)
def get_cheap_mobile_regions(db: Session = Depends(get_db)):
    f = open('Queries/cheap_mobile.sql', "r")
    query = f.read()
    f.close()
    regions_db = db.execute(text(query)).all()
    if not regions_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for the 'cheap_mobile' found")
    regions = [ region.region for region in regions_db ]
    return {'status': 'success', 'regions': regions}

# Get the latest datasource for the two most commonly appearing regions.
@router.get('/latest_datasources/', response_model=None)
def latest_datasources(db: Session = Depends(get_db)):
    f = open('Queries/latest_datasources.sql', "r")
    query = f.read()
    f.close()
    latest_datasources_db = db.execute(text(query)).all()
    if not latest_datasources_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No trips for the 'cheap_mobile' found")
    latest_datasources = [ { "region" : source.region, "latest_datasource" : source.datasource } for source in latest_datasources_db ]
    return {'status': 'success', 'latest_datasources': latest_datasources}

# Get a Plot showing the weekly average trips by region.
@router.get('/plot/', response_model=None)
def get_plot(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    #Get the existing regions
    regions_db = db.execute(text("SELECT region FROM trips GROUP BY region ORDER BY region ASC;")).all()
    if not regions_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No regions found")
    regions = []
    avgs = []
    for region in regions_db:
        #Get the weekly average for each region
        avg = get_weekly_average_trips_by_region(region.region, db)['weekly_average_trips']
        regions.append(region.region)
        avgs.append(avg)
    #Create the bar plot and return it.
    img_buf = create_bar(regions, avgs)
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="weekly_average_trips_by_region.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')

# Helper function to create the bar chart.
def create_bar(regs, avgs):
    x = np.array(regs)
    y = np.array(avgs)
    fig = plt.figure()
    plt.bar(x,y)
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    return img_buf

