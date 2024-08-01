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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

# Base.prepare(autoload_with = engine)
Base.prepare(autoload_with=engine, reflect=True)
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

# last 12 month variable
prev_year_date = '2016-08-23'
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
        f"/api/v1.0/temp/start/end"
        # f"/api/v1.0/&lt;start&gt;<br/>"
        # f"/api/v1.0/&lt;start&gt/&lt;end&gt"
    )
#Define route to retrieve stations
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Calculate the date  12 months from today
    todays_past = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # start_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= todays_past).all()
    session.close()
    #Convert the query results into a dictionary
    precip_dict = {date: prep for date, prep in precipitation_data}

    return jsonify (precip_dict)
   


#Define route to retrieve stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station, Station.name).all()
    session.close()
    #Convert the query results into dictionary
    stat_dict = [{"station":station, "name":name} for station, name in stations]

    return jsonify(stat_dict)
    
# Return a JSON list of Temperature Observations (tobs) for the previous year
# Adding routes for /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobstobs = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= prev_year_date).all()
    
    # most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # start_date = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    
    # temperature_data = session.query(Measurement.date, Measurement.tobs).\
    #     filter(Measurement.station == most_active_station, Measurement.date >= start_date).all()
    
    session.close()

    # temperature_dict = {date: tobs for date, tobs in temperature_data}
    return jsonify(tobstobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<date>")
def only_start(date):
    date_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    return jsonify(date_temp)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/temp/start/end")
def start_end(start,end):
    temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(temp_results)

# @app.route("/api/v1.0/<start>")
# def start_date(start):
#     session = Session(engine)
#     start_date = datetime.strptime(start, '%Y-%m-%d')
    
#     temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#         filter(Measurement.date >= start_date).all()
    
#     session.close()

#     temperature_stats = {"TMIN": temperature_data[0][0], "TAVG": temperature_data[0][1], "TMAX": temperature_data[0][2]}
#     return jsonify(temperature_stats)

# @app.route("/api/v1.0/<start>/<end>")
# def start_end_date(start, end):
#     session = Session(engine)
#     start_date = datetime.strptime(start, '%Y-%m-%d')
#     end_date = datetime.strptime(end, '%Y-%m-%d')
    
#     temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#         filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    
#     session.close()

#     temperature_stats = {"TMIN": temperature_data[0][0], "TAVG": temperature_data[0][1], "TMAX": temperature_data[0][2]}
#     return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)