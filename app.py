import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
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
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API done by An Bui!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Query for the date and precipitation for the last year
    result1 = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date <= last_date).filter(Measurement.date >= one_year ).\
    order_by(Measurement.date).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in result1}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    stations = session.query(Measurement.station).distinct().\
    order_by(Measurement.station).all()

    # Unravel results into a 1D array and convert to a list
    station_list = list(np.ravel(stations))
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    
    # Query the primary station for all tobs from the last year
    result2 = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.station =='USC00519281').\
    filter(Measurement.date < '2017-08-23').filter(Measurement.date > '2016-08-23').\
    order_by(Measurement.date).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(result2))

    # Return the results
    return jsonify(temps)


# @app.route("/api/v1.0/temp/<start>")
# @app.route("/api/v1.0/temp/<start>/<end>")
# def stats(start=None, end=None):
#     """Return TMIN, TAVG, TMAX."""

#     # Select statement
#     sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

#     if not end:
#         # calculate TMIN, TAVG, TMAX for dates greater than start
#         results = session.query(*sel).\
#             filter(Measurement.date >= start).all()
#         # Unravel results into a 1D array and convert to a list
#         temps = list(np.ravel(results))
#         return jsonify(temps)

#     # calculate TMIN, TAVG, TMAX with start and stop
#     results = session.query(*sel).\
#         filter(Measurement.date >= start).\
#         filter(Measurement.date <= end).all()
#     # Unravel results into a 1D array and convert to a list
#     temps = list(np.ravel(results))
#     return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
