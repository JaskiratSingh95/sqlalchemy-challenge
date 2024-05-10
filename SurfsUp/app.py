# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite://hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

# Base.prepare(autoload_with = engine)
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station= Base.classes.station
# Create our session (link) from Python to the DB

session = Session(engine)
#################################################git 
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt/&lt;end&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_date).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station).all()
    session.close()

    return jsonify(station_list)

# Adding routes for /api/v1.0/tobs, /api/v1.0/<start>, and /api/v1.0/<start>/<end>
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= start_date).all()
    
    session.close()

    temperature_dict = {date: tobs for date, tobs in temperature_data}
    return jsonify(temperature_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    temperature_stats = {"TMIN": temperature_data[0][0], "TAVG": temperature_data[0][1], "TMAX": temperature_data[0][2]}
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    
    session.close()

    temperature_stats = {"TMIN": temperature_data[0][0], "TAVG": temperature_data[0][1], "TMAX": temperature_data[0][2]}
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)