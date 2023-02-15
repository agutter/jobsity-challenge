from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import trip
from pydantic import BaseConfig

#Create the FastAPI app
app = FastAPI()
BaseConfig.arbitrary_types_allowed = True

#Set the allowed origins
origins = [
    settings.CLIENT_ORIGIN,
]

#Setup CORS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Include the router for the trips endpoints.
app.include_router(trip.router, tags=['Trips'], prefix='/api/trips')

#Include the router for the webhooks for async notifications.
#app.include_router(webhook.router, tags=['Webhooks'], prefix='/api/webhooks')

#Default healthcheck endpoint to test the app is running.
@app.get('/api/healthchecker')
def root():
    return {'message': 'Hello World'}

