DROP TABLE IF EXISTS trips;

CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    origin_coord POINT NOT NULL,
    destination_coord POINT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    datasource TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    origin_coord GEOMETRY(Point, 26910) NOT NULL,
    destination_coord GEOMETRY(Point, 26910) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    datasource TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    origin_coord_x FLOAT8 NOT NULL,
    origin_coord_y FLOAT8 NOT NULL,
    destination_coord_x FLOAT8 NOT NULL,
    destination_coord_y FLOAT8 NOT NULL,
    datetime TIMESTAMP NOT NULL,
    datasource TEXT NOT NULL
);

