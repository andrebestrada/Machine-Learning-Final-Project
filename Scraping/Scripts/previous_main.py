'''
Main script to run final project CAPP 30122. Crawls website, add distance to
metro stations and city center and make prediction.

Diego Escogar
Juan Vila
Camilo Arias
'''
import sys
sys.path.insert(0, 'Scripts/')
import crawler
import distances_to_houses as dist
import prediction
import map_visualize_1
import json
import pandas as pd


def crawl_scrape_distance(total_properties = float('inf'), prefix = 'test-'):
    '''
    Function that crawls the marketplace for mexico city. It scrapes the number
    of apartments and houses indicated at sale in Mexico City, and obtains for
    each property in the website, including variables like price, number of
    bedrooms, age, and latitude and longitude, among many others. It then
    assigns to each property the distance to the closes metro station, distance
    to city center, and the number of different public good within 5 km. It
    returns a json file of a list of dictionaries of all the properties. The
    crawl and scrape are done with the fuction go of the python script crawler,
    and the distance is calculated with the distance_calculator of the distances
    script.

    Inputs:
        total_properties: Int
        prefix: String to attach to files created
    Outputs:
        Json file of properties downloaded
        Json file of properties with distance meassures
    '''
    houses_df, num_houses = crawler.go('Distrito Federal', 'sale', 'houses',
                                       './Intermediate_Files/' + prefix + 'houses_df.json',
                                       total_properties)
    aparts_df, num_apts = crawler.go('Distrito Federal', 'sale', 'apartments',
                                     './Intermediate_Files/' + prefix + 'apartments_df.json',
                                     total_properties)
    properties_df = houses_df + aparts_df
    with open("./Intermediate_Files/" + prefix + "properties_df.json", 'w') as fp:
        json.dump(properties_df, fp)

    dist.distance_calculator("./Intermediate_Files/" + prefix + "properties_df.json",
                                  "./Intermediate_Files/" + prefix + "properties_with_dist.json")


def predict(properties_file="./Intermediate_Files/results_with_metrodata.json"):
    '''
    Function that takes the json file of all the marketplace of metroscubicos
    crawled and scrapped and with the distance assigned (The result of running
    the crawl_scrape_distance function fith the default parameter), and trains
    three predictive machine learning models with 2/3 of the dataset to predict
    the remaining 1/3. 

    Inputs:
        total_properties_file: JSON file. 
    Outputs:
        Json file with properties with real price, linear model, nd the three 
        predicted prices.
    '''
    predictions = prediction.go(properties_file)
    predictions.to_json('./Intermediate_Files/predictions_data')

    return predictions


def visualize():
    '''

    '''
    map_visualize_1.prices_map()
    predictions = pd.read_json('./Intermediate_Files/predictions_data')    
    map_visualize_1.kdensity_predictions(predictions)
