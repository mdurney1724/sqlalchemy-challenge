from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
 
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    one_year_ago = (pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
   
    results = session.query(Station.station).all()
    
    stations_list = list(np.ravel(results))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the previous year for the most active station."""
  
    most_active_station_id = 'USC00519281'
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    one_year_ago = (pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
   
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start=None, end=None):
    """Return the minimum, average, and maximum temperatures for a specified date range."""
    
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]
    
    if not end:
       
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    temps = list(np.ravel(results))
    
    return jsonify({"TMIN": temps[0], "TAVG": temps[2], "TMAX": temps[1]})

if __name__ == '__main__':
    app.run(debug=True)