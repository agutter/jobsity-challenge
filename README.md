# Jobsity Challenge
This project contains the Jobsity Data Engineering Tech Challenge.

## Assignment
Your task is to build an automatic process to ingest data on an on-demand basis. The data represents trips taken by different vehicles, and include a city, a point of origin and a destination.
This CSV file gives you a small sample of the data your solution will have to handle. We would like to have some visual reports of this data, but in order to do that, we need the following
features.
We do not need a graphical interface. Your application should preferably be a REST API, or a console application.

## Technical Stack and Scalability
To create the data pipeline we used FastAPI along SQLAlchemy to create a REST API with an ORM backend to handle the database connections and modelling. A PostgreSQL 15 database was created using Docker to store the data.

FastAPI provides scalability, as detailed in its [official documentation](https://fastapi.tiangolo.com/benchmarks/). The API has three different input methods, two using JSON as input format and a third which receives a CSV file.
In order to return the generated IDs and allow for better testing, the JSON endpoints process each trip individually, while the CSV endpoints uses a bulk_save method to store all the uploaded trips faster. This is then ideal method to ingest data and should prove easily scalable. Tested with up to 10000 records (*Data/long.csv*), the API responded in less than a second.
Additionally, PostgreSQL proves to be one of the most effective database engines and should be scalable up to 100 million records without any issues.

Alembic was used to handle the DB creation and migrations, and Pydantic allowed validation of the data for the endpoints.

## Issues
The use of PostGIS for Geometrical Data Types proved to be harder than anticipated, with several compatibility issues and complicated data types which proved hard to handle in the model.
Because of this, the endpoints have to process the data as strings and parse them to their proper objects, which impacts performance and makes for less clear code.

The Point datatype, however, proves very beneficial and allows for some PostGIS methods to analyze the proximity of two points, or whether a point in contained in an area. With more time these issues would have been able to be sorted out, resulting in a far simpler code which should work better.

## Decisions
The similarity between trips ended up being quite more complex than expected to analyze, and a proper clustering algorithm would have been far longer than reasonable. A choice was then made to consider for each point a cluster of its closest neighbors, which would then be used to group the results. If two points have the same cluster, they are close to each other and should be consider similar. An arbitrary value of 1.5 was chosen for the maximum distance between neighbors, though it should be adjusted after reviewing the results. For the datetimes, it was considered two trips matched if they happened in the same minute. The next trunc available would have been by the hour which seemed excessive given the distance a car travels in that time.

## Endpoints
The API has three input endpoints, as well as several endpoints to check the results. The vast majority of them return the full results as stored in the database without considering similarity given the complexity of the algorithm to find neighbors and the fact we lose partial information while doing so. With more time it should be possible to find a middle point, and possibly decide which of the endpoints should consider similarity.

For the weekly averages, two endpoints were created, one for region and another for bounding box, given the different approach needed. The logic was included in two queries in the **Queries** folder, along the bonus queries, given it proved too complex to handle exclusively through SQLAlchemy.
Two additional endpoints are available as well to consume the bonus queries, one of which could have been parametrized to consider any datasource and not only the *'cheap_mobile'*.

Finally, an endpoint was created to return a Bar plot showing the average weekly trips for each region that appears in the data.

## Polling and webhooks
There wasn't enought time to properly test implementing webhooks to handle asynchronous notifications, but that would have been the chosen approach. The REST API, however, doesn't seem to be an issue in this subject, given the fast response times.

## Cloud
The application is relatively simple and could be set up on a single VM or cluster node. However, the best approach to ensure scalability and security would be to split up the REST API and the database, giving them independent resources. This would require obviously authentication and security considerations which weren't implemented give the simplicity of the project, though FastAPI allows for an easy set up.

## Running the project
Both the API and the Database are dockerized, allowing for an easy installation and execution. After cloning the GIT Repo, it should be enough to initialize the virtual environment, download any required packages and simply running docker-compose.

The basic instructions would then be:

---------- Clone the repository and activate the virtual environment ----------
git clone https://github.com/agutter/jobsity-challenge
cd jobsity-challenge
python3 -m venv venv
source venv/bin/activate

---------- Install the required packages and create the .env file --------------
sudo apt-get install postgresql proj-bin qgis postgis postgresql-15-postgis-3
pip install -r requirements.txt
cp .env.sample .env

------------------------------ Start the Database ------------------------------
sudo docker-compose build --no-cache
sudo docker-compose up -d

-------------------------------- Enable PostGIS --------------------------------
sudo docker exec -it postgres bash
psql -U postgres jobsity
SELECT * FROM pg_available_extensions;
CREATE EXTENSION postgis;

----------------------------- Create the Trips table ----------------------------
alembic upgrade head

--------------------------------- Start the API ---------------------------------
uvicorn app.main:app --host localhost --port 8000 --reload

The API can be tested either with a utility like Postman or directly through the browser with the autogenerated FastAPI Docs at [http://localhost:8000/docs].
The *Data/* directory contains the provided sample CSV, another CSV which replicates it up to 10000 records, and a sample json file with the structure to test the JSON input endpoints.

