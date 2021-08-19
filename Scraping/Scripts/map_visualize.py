"""
Mapping properties

Diego Escogar
Juan Vila
Camilo Arias
'''

"""
import json
import pandas as pd
import geopandas # Install if necessary
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns

def prices_map(file="./Intermediate_Files/properties_df.json", graph_name='prices_map'):
    '''
    Construct map to show the distribution of prices across CDM.
    Input: json file with prices data
    Output: graph
    '''
    #Reading properties json
    with open(file) as f:
        properties = json.load(f)

    properties_df = pd.DataFrame(properties)
    print(properties_df.head())
    properties_df = properties_df[['price', 'latitude', 'longitude']]
    properties_df = properties_df.apply(pd.to_numeric)
    properties_df.dropna(inplace = True)

    #Filtering properties with wrong latitude/longitude
    properties_df = properties_df[properties_df['latitude'] < 19.60]
    properties_df = properties_df[properties_df['latitude'] > 19.15]
    properties_df = properties_df[properties_df['longitude'] > -99.34]
    properties_df = properties_df[properties_df['longitude'] < -98.93]
    properties_df = properties_df[properties_df['price'] < 10000000]
    print("line1")

    #Reading SHP of Mexico City
    cdmx_link = './Intermediate_Files/cdmx_shapefile/09a.shp'  
    cdmx = geopandas.read_file(cdmx_link)
    cdmx_wsg84 = cdmx.to_crs({'init': 'epsg:4326'}) #Changing projection system
    print("line2")
    #Transforming properties_df to geodatabase
    properties_df['Coordinates'] = list(zip(properties_df.longitude, \
        properties_df.latitude))
    properties_df['Coordinates'] = properties_df['Coordinates'].apply(Point)
    gdf = geopandas.GeoDataFrame(properties_df, geometry='Coordinates')
    gdf.crs = {'init' :'epsg:4326'}
    print("line3")

    #Plotting
    fig, ax = plt.subplots(1, figsize = (10, 6))

    #ax.set_aspect('equal')

    cdmx_wsg84.plot(ax=ax, color='None', edgecolor='black')

    gdf.plot(ax=ax, marker='.', markersize=2, column = 'price', cmap='viridis')
    ax.axis('off')

     # Create colorbar
    vmin = gdf['price'].min()
    vmax = gdf['price'].max()
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=vmin, \
        vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm)
    plt.savefig('./Intermediate_Files/' + graph_name)
    plt.show()
    plt.clf()


def kdensity_predictions(y_hat, graph_name='graph_kdensity'):
    '''
    Generates visualization for the predictions data densities
    Input:  prediction for each method (list of arrays)
    Output: graph
    '''
    # Densities:
    fig2, axis_ = plt.subplots()
    sns.set(color_codes=True)
    sns.set_style('whitegrid')
    sns.kdeplot(y_hat[0], color="g", shade=True, ax=axis_, label="Data")
    sns.kdeplot(y_hat[1], color="r", ax=axis_, label="Linear Model")
    sns.kdeplot(y_hat[2], color="b", ax=axis_, label="LASSO")
    sns.kdeplot(y_hat[3], color="purple", ax=axis_, label="Decision Tree")
    sns.kdeplot(y_hat[4], color="orange", ax=axis_, label="Random Forest")
    plt.xlim(0,1000000)
    plt.ylabel('Density', fontsize=18)
    plt.xlabel('Predicted Price', fontsize=18)
    fig2.show()
    plt.savefig('./Intermediate_Files/' + graph_name)
    plt.close(fig2) 
