import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
# -----------------------------------
# Flask mode: ON for all web framework
app = Flask(__name__)

# SQL database setup to pull stored data----------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)
# ------------------------------------
# Assign python variables for key db objects
Samples_Metadata = Base.classes.sample_metadata
Samples = Base.classes.samples

# Welcome page------------------------


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")
# here is Mozilla Firefox connection info
#   Response Headers-----------
    # Content-Length	1040
    # Content-Type	application/json
    # Date	Mon, 17 Dec 2018 07: 14: 26 GMT
    # Server	Werkzeug/0.14.1 Python/3.6.5
# ----------------------------
# Accept /html, application/xhtml+xml, application/xml
# q = 0.9, */*
# q = 0.8
# Accept-Encoding	gzip, deflate
# Accept-Language	en-US, en
# q = 0.5
# Connection	keep-alive
# Host	127.0.0.1: 5000
# Upgrade-Insecure-Requests	1
# User-Agent	Mozilla/5.0 (Windows NT 10.0 Win64 x64 rv: 64.0)
# Gecko/20100101 Firefox/64.0


@app.route("/names")
def names():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return a list of the column names (sample names)
    return jsonify(list(df.columns)[2:])


@app.route("/metadata/<sample>")
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.ETHNICITY,
        Samples_Metadata.GENDER,
        Samples_Metadata.AGE,
        Samples_Metadata.LOCATION,
        Samples_Metadata.BBTYPE,
        Samples_Metadata.WFREQ,
    ]

    results = db.session.query(
        *sel).filter(Samples_Metadata.sample == sample).all()

    # Create a dictionary entry for each row of metadata information
    sample_metadata = {}
    for result in results:
        sample_metadata["sample"] = result[0]
        sample_metadata["ETHNICITY"] = result[1]
        sample_metadata["GENDER"] = result[2]
        sample_metadata["AGE"] = result[3]
        sample_metadata["LOCATION"] = result[4]
        sample_metadata["BBTYPE"] = result[5]
        sample_metadata["WFREQ"] = result[6]

    print(sample_metadata)
    return jsonify(sample_metadata)


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]
    # Format the data to send as json
    data = {
        "otu_ids": sample_data.otu_id.values.tolist(),
        "sample_values": sample_data[sample].values.tolist(),
        "otu_labels": sample_data.otu_label.tolist(),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()
