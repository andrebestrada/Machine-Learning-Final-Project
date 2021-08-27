from flask import Flask, jsonify
from flask import request
from flask import Response
from flask import render_template
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
import pandas as pd
from sklearn import metrics

application = Flask(__name__)

# Function that receives data from AWS Bucket
def data_loading():
    # national_data = pd.read_json('https://national-data.s3.amazonaws.com/national_data_final.json')
    national_data = pd.read_json('https://national-data.s3.amazonaws.com/national_data_complete.json')
    national_data.rename(columns={'Superficie construida':'Superficie m2','Cuota mensual de mantenimiento':'Cuota Mantenimiento'}, inplace=True)
    national_data = national_data.fillna(0)

    national_data = national_data[national_data['currency']=='MXN']
    national_data = national_data[national_data['name'].str.contains('Renta')==False]
    national_data = national_data[national_data['cp'].isnull()==False]

    args = request.args

    for k, v in args.items():
        if k == "State" and v != '':
            national_data = national_data[national_data['Estado']==v]
        if k == "Min_price" and v != '':
            national_data = national_data[national_data['price'] > float(v)]
        if k == "Max_price" and v != '':
            national_data = national_data[national_data['price'] < float(v)]
        if k == "Min_surface" and v != '':
            national_data = national_data[national_data['Superficie total'] > float(v)]
        if k == "Max_surface" and v != '':
            national_data = national_data[national_data['Superficie total'] < float(v)]
        if k == "Min_rooms" and v != '':
            national_data = national_data[national_data['Recamaras'] > float(v)]
        if k == "Max_rooms" and v != '':
            national_data = national_data[national_data['Recamaras'] < float(v)]
        if k == "Min_enviroments" and v != '':
            national_data = national_data[national_data['Ambientes'] > float(v)]
        if k == "Max_enviroments" and v != '':
            national_data = national_data[national_data['Ambientes'] < float(v)]
                    

    return national_data

# Function Splits Data and Transforms Categorical Values with One Hot Encoding
def split_and_encoding(data):
    X_full = data
    y = X_full.price
    features = ['type_of_prop','cp','Superficie m2', 'Ambientes', 'Recamaras', 'Banos','Estacionamientos', 'Antiguedad', 'Cantidad de pisos','Cuota Mantenimiento', 'Bodegas']
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

# Function that receives a data set and a model, fits the model and return performance measures
def machine_learning_model(data, model):
    OH_X_train, OH_X_valid, y_train, y_valid = split_and_encoding(data)

    # Fit Model
    model.fit(OH_X_train, y_train)
    prediction = model.predict(OH_X_valid)
 
    #Performance Metrics 
    mae = round(mean_absolute_error(y_valid, prediction),2)
    score = round(model.score(OH_X_valid, y_valid)*100,2)
    mape = round((np.mean(np.abs((y_valid - prediction) / np.abs(y_valid)))),2)
    acc = round(100*(1 - mape), 2)
    mape = round(mape * 100, 2)
    rmse = np.sqrt(metrics.mean_squared_error(y_valid, prediction))

    # Feature Importance
    importances_round=[]
    importances=model.feature_importances_

    for x in importances:
        importances_round.append(round(x,2))
    
    print(importances_round)

    df = pd.DataFrame({'Features':OH_X_valid.columns, 'Importance':importances_round}).reset_index(drop=True)

    try:
        weight = float(float(df[df.iloc[:, 0] == 0]['Importance']))+float(float(df[df.iloc[:, 0] == 1]['Importance']))
    except Exception as e:
        weight = float(float(df[df.iloc[:, 0] == 0]['Importance']))

    new_row = pd.DataFrame({'Features':'Tipo','Importance':weight},index=[13])
    df = df.append(new_row)
    
    df.drop(labels=df[df.iloc[:, 0] == 1].index, axis=0, inplace=True)
    df.drop(labels=df[df.iloc[:, 0] == 0].index, axis=0, inplace=True)
    df.sort_values("Importance", ascending=False, inplace=True)
    df = df.reset_index(drop=True)
    dict_df = df.to_dict()
    
    # Dictionarie with results
    results={'mae':mae,
             'mape':mape,
             'accuracy':acc,
             'rmse':rmse,
             'features_importance': dict_df,
            #  'box_prices':box_prices
            }

    print(results)
    return results, model

@application.route("/")
def index():
    return render_template('index.html')

@application.route("/tableau")
def index2():
    return render_template('tableau.html')

@application.route("/comparison")
def index3():
    return render_template('comparison.html')

@application.route("/dropdowns")
def dropdowns():
    
    national_data = data_loading()
    
    states = national_data["Estado"].unique()
    # states = np.insert(states,0,"")

    dropdowns= pd.DataFrame.from_dict({'states':[states]})

    response = Response(dropdowns.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@application.route("/results")
def results():
    print("Its Alive :D")

    #################################################################################
    # Get Parameters
    args = request.args

    #################################################################################
    # Loading Data
    national_data = data_loading()
   
    #################################################################################
    # Define model
    model = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)

    #################################################################################
    # Machine Learning Function
    results, model = machine_learning_model(national_data, model)

    #################################################################################
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@application.route("/boxes")
def boxes():
    # state = request.args.get("State")
    data = data_loading()

    box_data={'box_price':[data['price']],
                'box_surface':[data['Superficie total']],
                'box_room':[data['Recamaras']],
                'box_enviroment':[data['Ambientes']]
                }

    box_data = pd.DataFrame.from_dict(box_data)
    
    response = Response(box_data.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

    
@application.route("/prediction")
def prediction():
    #################################################################################
    # Loading Data
    national_data = data_loading()
   
    #################################################################################
    # Define model
    model = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)

    #################################################################################
    # Machine Learning Function
    results, model = machine_learning_model(national_data, model)
    
    import statistics
    
    cp_default = statistics.median(national_data['cp'])
    room_default = statistics.median(national_data['Recamaras'])
    bathroom_default = statistics.median(national_data['Banos'])
    enviroment_default = statistics.median(national_data['Ambientes'])
    surface_Cons_default = statistics.median(national_data['Superficie m2'])
    parkinglot_default = statistics.median(national_data['Estacionamientos'])

    antiguedad_default = statistics.median(national_data['Antiguedad'])
    surfaceTot_default = statistics.median(national_data['Superficie total'])
    mantenimiento_default = statistics.median(national_data['Cuota Mantenimiento'])
    bodegas_default = statistics.median(national_data['Bodegas'])
    floor_default = statistics.median(national_data['Cantidad de pisos'])
    

    # cp_default = national_data['cp'].mode()
    # surfaceTot_default = national_data['Superficie total'].mode()
    # room_default = national_data['Recamaras'].mode()
    # bathroom_default = national_data['Banos'].mode()
    # surface_Cons_default = national_data['Superficie construida'].mode()
    # parkinglot_default = national_data['Estacionamientos'].mode()

    # Default inputs
    # antiguedad_default = national_data['Antiguedad'].mode()
    # enviroment_default = national_data['Ambientes'].mode()   
    # mantenimiento_default = national_data['Cuota mensual de mantenimiento'].mode()
    # bodegas_default = national_data['Bodegas'].mode()
    # floor_default = national_data['Cantidad de pisos'].mode()

    house_default = 1
    apartment_default = 0


    args = request.args
    
    for k, v in args.items():
        if k == "postal_code" and v != '':
            cp_default = v
        if k == "enviroments" and v != '':
            enviroment_default = v
        if k == "rooms" and v != '':
            room_default = v
        if k == "bathrooms" and v != '':
            bathroom_default = v
        if k == "constructed_surface" and v != '':
            surface_Cons_default = v
        if k == "parking_lots" and v != '':
            parkinglot_default = v
        if k == "type" and v != '':
            if v == '0':
                house_default = 0
                apartment_default = 1
   
    
    input_prediction = pd.DataFrame()
    input_prediction = pd.DataFrame({'cp':cp_default, 'Superficie m2':surface_Cons_default,'Recamaras': room_default, 
                                 'Estacionamientos': parkinglot_default, 'Cantidad de pisos':floor_default,
                                 'Bodegas':bodegas_default, 'Ambientes':enviroment_default,
                                 'Banos':bathroom_default, 'Antiguedad':antiguedad_default, 'Cuota Mantenimiento':mantenimiento_default,
                                '0':house_default,'1':apartment_default},index=[0]) 
    print(input_prediction)

    prediction_result = model.predict(input_prediction)
    results = pd.DataFrame({'Prediction':prediction_result[0]},index=[0])
    
    response = Response(results.to_json(orient="records"), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response




if __name__ == "__main__":
    application.run(debug=True)