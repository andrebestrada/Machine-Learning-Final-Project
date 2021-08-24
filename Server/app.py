from flask import Flask, jsonify
#from flask_pymongo import PyMongo
from flask import request
from flask import Response
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
import dateutil
import pandas as pd
import os
import json

# OH_X_train=[][]
# OH_X_valid=[][]
# y_train=[][]
# y_valid=[][]

app = Flask(__name__)

#mongo_db = "Spotifydb"
#mongo = PyMongo(app, uri=f'mongodb://localhost:27017/{mongo_db}')
#collection = mongo.db.Top200byCountry

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

# Function that receives data and a ML model and return Performance Results

def data_loading():
    national_data = pd.read_json('https://national-data.s3.amazonaws.com/national_data_final.json')

    national_data = national_data[national_data['currency']=='MXN']
    national_data = national_data[national_data['name'].str.contains('Renta')==False]
    national_data = national_data[national_data['cp'].isnull()==False]

    national_data = national_data[national_data['price']>1000000]
    national_data = national_data[national_data['price']<10000000]
    national_data = national_data[national_data['Superficie total']<300]

    return national_data



def split_and_encoding(data):
    
    X_full = data
    y = X_full.price
    features = ['type_of_prop','cp', 'Superficie total','Superficie construida', 'Ambientes', 'Recamaras', 'Banos','Estacionamientos', 'Antiguedad', 'Cantidad de pisos','Cuota mensual de mantenimiento', 'Bodegas']
    X = X_full[features]
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=0)

    #One Hot Encoding  
    s = (X_train.dtypes == 'object')
    object_cols = list(s[s].index)
    OH_encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
    OH_cols_train = pd.DataFrame(OH_encoder.fit_transform(X_train[object_cols]))
    OH_cols_valid = pd.DataFrame(OH_encoder.transform(X_valid[object_cols]))
    OH_cols_train.index = X_train.index
    OH_cols_valid.index = X_valid.index
    num_X_train = X_train.drop(object_cols, axis=1)
    num_X_valid = X_valid.drop(object_cols, axis=1)
    OH_X_train = pd.concat([num_X_train, OH_cols_train], axis=1)
    OH_X_valid = pd.concat([num_X_valid, OH_cols_valid], axis=1)

    # Remove NAs
    OH_X_train=OH_X_train.fillna(0)
    OH_X_valid=OH_X_valid.fillna(0)

    return OH_X_train, OH_X_valid, y_train, y_valid


def machine_learning_model(data, model):
    OH_X_train, OH_X_valid, y_train, y_valid = split_and_encoding(data)

    # Fit Model
    model.fit(OH_X_train, y_train)
    prediction = model.predict(OH_X_valid)
 
    #Performance Metrics 
    mae = round(mean_absolute_error(y_valid, prediction),2)
    score = round(model.score(OH_X_valid, y_valid)*100,2)
    mape = round(np.mean(np.abs((y_valid - prediction) / np.abs(y_valid))),2)
    acc = round(100*(1 - mape), 2)


    

    
    # Feature Importance
    df = pd.DataFrame({'Features':OH_X_valid.columns, 'Importance':model.feature_importances_}).reset_index(drop=True)
    weight = float(float(df[df.iloc[:, 0] == 0]['Importance']))+float(float(df[df.iloc[:, 0] == 1]['Importance']))
    new_row = pd.DataFrame({'Features':'Tipo','Importance':weight},index=[13])
    df = df.append(new_row)

    df.drop(labels=df[df.iloc[:, 0] == 1].index, axis=0, inplace=True)
    df.drop(labels=df[df.iloc[:, 0] == 0].index, axis=0, inplace=True)
    df.sort_values("Importance", inplace=True)
    dict_df = df.to_dict()

    print("step 2")

    # Dictionarie with results
    results={'mae':mae,
             'mape':mape,
             'accuracy':acc,
             'score':score,
             'features_importance': dict_df
            }

    return results


@app.route("/dropdowns")
def dropdowns():

    national_data = data_loading()
   
    states = national_data["Estado"].unique()
    # states = np.insert(states,0,"")

    dropdowns= pd.DataFrame.from_dict({'states':[states]})

    response = Response(dropdowns.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route("/results")
def results():
    print("Its Alive :D")

    #################################################################################
    # Get Parameters
    state = request.args.get("State")

    #################################################################################
    # Loading Data
    national_data = data_loading()
   
    #################################################################################
    # Define model
    model = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)

    #################################################################################
    # Machine Learning Function
    data = national_data[national_data['Estado']==state]
    results = machine_learning_model(data, model)

    #################################################################################
    # Features Importance


    #################################################################################
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/features")
def features():
    state = request.args.get("State")

    national_data = data_loading()

    model = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)



    



# @app.route("/songs")
# def jsonified():

#     group = request.args.get("Group_by")

#     songs = [i for i in collection.find(filter_data())]    
#     for song in songs: song.pop("_id")

#     # This is commented only for testing
#     # response = jsonify(songs)
#     # response.headers.add('Access-Control-Allow-Origin', '*')
#     # return response
#     response = group_data(songs, group,"Streams",[group,"Streams"]) 

#     return response


# @app.route("/streamsbydate")
# def jsonified2():
#     group = request.args.get("Group_by")

#     songs = [i for i in collection.find(filter_data())]    
#     for song in songs: song.pop("_id")

#     data_df = pd.DataFrame(songs)
#     grouped = data_df.groupby(group).sum().reset_index()
#     grouped["MonthYear"] = (grouped['MonthYear'].dt.strftime('%b')).astype(str)+" "+(pd.DatetimeIndex(grouped['MonthYear']).year).astype(str)
    
#     response = Response(grouped.to_json(orient="records"), mimetype='application/json')
#     response.headers.add('Access-Control-Allow-Origin', '*')

#     return response

# @app.route("/summary")
# def jsonified3():
#     songs = [i for i in collection.find(filter_data())]    
#     for song in songs: song.pop("_id")

#     data_df = pd.DataFrame(songs)
    
#     country_array=[]
#     artist_array=[]
#     song_array=[]

#     country_array = (data_df["Country"].unique())
#     country_array = np.insert(country_array,0,"")

#     artist_array = np.insert(((data_df["Artist"].unique())[0:500]),0,"")
#     song_array = np.insert(((data_df["Track_Name"].unique())[0:500]),0,"")

#     no_artist = len(data_df["Artist"].unique())
#     no_songs = len(data_df["Track_URL"].unique())
#     total_streams = data_df["Streams"].sum()

#     summary= pd.DataFrame.from_dict({'ArtistCount':[no_artist],'SongsCount':[no_songs],'TotalStreams':[total_streams],'Countries':[country_array],'Artists':[artist_array],'Songs':[song_array]})

#     response = Response(summary.to_json(orient="records"), mimetype='application/json')
#     response.headers.add('Access-Control-Allow-Origin', '*')

#     return response

# @app.route("/Popularity")
# def jsonified4():
    
#     songs = [i for i in mongo.db.TopGlobal.find()]    
#     for song in songs: song.pop("_id")

#     # This is commented only for testing
#     response = jsonify(songs)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response



if __name__ == "__main__":
    app.run(debug=True)