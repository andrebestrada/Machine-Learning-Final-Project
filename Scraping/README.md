# Crawler and Scrapper of metroscubicos.com

This code crawls the webpage metroscubicos.com and scrapes the information of the properties listed (Including, but not limited to, price, number of rooms, number of bathrooms, area, latitude and longitude). The user needs to specify location (State), type of property (houses or apartments), the type of offer (sale or rent), and an optional limit of properties to download. The script mainly relies on the use of requests and parsing html with beautifulsoup. It created a JSON file of the properties.

## Required libraries:
- numpy 1.15.4
- pandas 0.24.2
- beautifulsoup4 4.7.1
- matplotlib 3.0.3
- geopandas 0.4.0+67.g08ad2bf
- shapely 1.6.4.post2
- requests 2.21.0

## How to run the code:

From terminal run: python crawler.py <'State'> <'type_of_offer'> <'type_of_property'> <'outputJSON'> <'limit'(optional)>

Examples: 

- Download the first 10 houses at sale in Distrito Federal:

python crawler.py 'Distrito Federal' 'sale' 'houses' '/Users/camiloariasm/houses_df.json' 10

- Download all apartments at rent in the State of Mexico:

python crawler.py 'Estado de Mexico' 'rent' 'apartments' '/Users/camiloariasm/apartments_edomex.json' 10


## Description of the python scripts:


Crawler.py: Crawler and scrapper of the marketplace. It obtains all the
characteristics listed of the properties in the market, including price
number of rooms, number of bedrooms, amenities, location, area, etc.

It uses two classes: a Market class, which represents the market that results
from a search on the webpage, and a Crawler class, which represents a crawler 
of the market.

metroscubicos.com only displays 2000 results per search, even if the total number
of properties listed for a given search is more than that number. To overcome this,
the crawler is performed recursivelly. If the initial search has more than 2000 
results, the crawler recursivelly builds submarkets by applying filters. The result
of this is a structure similar to a "tree" of markets. With this structure, the market
crawl is also performes recursivelly, crawling and scrapping those markets that do not
have submarkets. 
