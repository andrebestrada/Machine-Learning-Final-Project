from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask import request
from flask import Response
import pandas as pd
import numpy as np
import dateutil

app = Flask(__name__)

mongo_db = "Spotifydb"

mongo = PyMongo(app, uri=f'mongodb://localhost:27017/{mongo_db}')

collection = mongo.db.Top200byCountry
# collection = mongo.db.Top200byCountry

# This function receives some parameters that will be used to group by and summarize the data 
def group_data(data,column,value,headers):
    data_df = pd.DataFrame(data)

    grouped = data_df.groupby(column).sum().sort_values(by=[value],ascending=False).reset_index()
    grouped = grouped[headers]

    response = Response(grouped.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

# Function that retrieves parameters from end point and uses them to create an array of objects that will be used to filter data from Mongo
def filter_data():
    filters={}
    date_filter={}
    args = request.args
    for k, v in args.items():
        
        if(v != "" and k != 'Group_by'): 
            if(k == 'datefrom' or k == 'dateto'): 
                if(k == 'datefrom'):
                    date_filter['$gte'] = dateutil.parser.parse(v)
                    filters["Date"] = date_filter
                if(k == 'dateto'):
                    date_filter['$lt'] = dateutil.parser.parse(v)
                    filters["Date"] = date_filter
            else:
                filters[k] = v
    
    return filters

@app.route("/songs")
def jsonified():

    group = request.args.get("Group_by")

    songs = [i for i in collection.find(filter_data())]    
    for song in songs: song.pop("_id")

    # This is commented only for testing
    # response = jsonify(songs)
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # return response
    response = group_data(songs, group,"Streams",[group,"Streams"]) 

    return response


@app.route("/streamsbydate")
def jsonified2():
    group = request.args.get("Group_by")

    songs = [i for i in collection.find(filter_data())]    
    for song in songs: song.pop("_id")

    data_df = pd.DataFrame(songs)
    grouped = data_df.groupby(group).sum().reset_index()
    grouped["MonthYear"] = (grouped['MonthYear'].dt.strftime('%b')).astype(str)+" "+(pd.DatetimeIndex(grouped['MonthYear']).year).astype(str)
    
    response = Response(grouped.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/summary")
def jsonified3():
    songs = [i for i in collection.find(filter_data())]    
    for song in songs: song.pop("_id")

    data_df = pd.DataFrame(songs)
    
    country_array=[]
    artist_array=[]
    song_array=[]

    country_array = (data_df["Country"].unique())
    country_array = np.insert(country_array,0,"")

    artist_array = np.insert(((data_df["Artist"].unique())[0:500]),0,"")
    song_array = np.insert(((data_df["Track_Name"].unique())[0:500]),0,"")

    no_artist = len(data_df["Artist"].unique())
    no_songs = len(data_df["Track_URL"].unique())
    total_streams = data_df["Streams"].sum()

    summary= pd.DataFrame.from_dict({'ArtistCount':[no_artist],'SongsCount':[no_songs],'TotalStreams':[total_streams],'Countries':[country_array],'Artists':[artist_array],'Songs':[song_array]})

    response = Response(summary.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/Popularity")
def jsonified4():
    
    songs = [i for i in mongo.db.TopGlobal.find()]    
    for song in songs: song.pop("_id")

    # This is commented only for testing
    response = jsonify(songs)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response



if __name__ == "__main__":
    app.run(debug=True)