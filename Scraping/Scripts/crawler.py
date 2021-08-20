'''
Crawler of metroscubicos.com for final project of CAPP 30122

Diego Escogar
Juan Vila
Camilo Arias
'''
import re
import ast
import queue
import time
import json
import bs4
import util
import sys


def get_soup(url):
    '''
    Returns the soup of the current_market_url.
    Inputs:
        url: str
    Output:
        BeautifulSoup object
    '''
    time.sleep(0.05)
    url_request = util.get_request(url)
    if not url_request:
        return False
    html = util.read_request(url_request)
    if not html:
        return False
    return bs4.BeautifulSoup(html, "html5lib")


class Market:
    '''
    Class to define a real estate market, defined by estate, purchase or rent,
    houses or apartments, the url of the market and the level of recursion.
    '''
    DOMAIN = "https://inmuebles.metroscubicos.com"

    def __init__(self, state, type_of_offer, type_of_prop, url=None, level=0):
        '''
        Recursive initializer of the Market class.
        Inputs:
            state: (State of Mexico) str
            type_of_offer: ('sale' or 'rent') str
            type_of_prop: ('houses' or 'apartments') str
            url: str
            level: int
        '''
        assert type_of_offer in ("sale", "rent"),\
            "Type of offer must be 'sale' or 'rent'"

        assert type_of_prop in ("houses", "apartments"),\
            "Type of prop must be 'houses' or 'apartments'"

        self.level = level
        self.state = state
        self.label = state
        if self.level > 0:
            self.label = url.split("/")[-2] if url[-1] == "/" else\
                         url.split("/")[-1]
        print("Creating market for {}".format(self.label))
        self.type_of_offer = type_of_offer
        self.type_of_prop = type_of_prop

        self.market_url = url if url else self.get_market_url()
        print("=> URL {}".format(self.market_url))
        self.submarkets, self.num_props = self.get_sub_markets()
        self.crawler = None


    def get_market_url(self):
        '''
        Construct the base market url from the domain, the type of property,
        type of offer and the state of Mexico.
        Output:
            string
        '''
        type_of_offer_transl = {'sale':'venta',
                                'rent':'renta'}
        type_of_prop_transl = {'houses':'casas',
                               'apartments':'departamentos'}
        oferta = type_of_offer_transl[self.type_of_offer]
        propiedad = type_of_prop_transl[self.type_of_prop]
        estado = ('-').join(self.state.lower().split(' '))
        print("-----------------------------------------------------------")
        print("/".join([self.DOMAIN, propiedad, oferta, estado]) + "/")
        print("-----------------------------------------------------------")
        return "/".join([self.DOMAIN, propiedad, oferta, estado]) + "/"
        #Last slash very important to get filters by city


    def get_sub_markets(self):
        '''
        In case the number of properties in the market is more than 2000,
        which is the maximum number of properties displayed each market,
        it returns a list of sub city markets if current market is a
        state market, or sub markets by price ranges else.
        Returns empty list if num of results < 2000.
        Output:
            (list of sub markets, total number of properties)
        '''
        market_soup = get_soup(self.market_url)
        
        if not market_soup:
            return (None, 0)
        total_properties = get_total_results(market_soup)

        total_properties = total_properties if total_properties else 0

        if total_properties <= 40 * 48:
            #Max pages displayed * properties per page
            return ([], total_properties)

        submarkets = []
        
        if self.level == 0:
            submarkets_str = market_soup.find(attrs={"aria-label": "Ciudades"})
        elif self.level == 1:
            submarkets_str = market_soup.find(attrs={"aria-label": "Precio"})
        elif self.level == 2:
            submarkets_str = market_soup.find(attrs={"aria-label": "Superficie total"})
        
        #print(f' ### {submarkets_str} ###') 
        if submarkets_str:
            submarkets_seen = set()
            #print(f'1 ======================> {submarkets_seen}')
            for tag in submarkets_str.find_all('a'):
                submarket_url = tag['href']
                #print(f'2 ======================> {submarket_url} ====')
                if submarket_url not in submarkets_seen:
                    #print("*** SI ENTRO ***")
                    submarkets_seen.add(submarket_url)
                    submarkets.append(Market(self.state, self.type_of_offer,
                                             self.type_of_prop,
                                             submarket_url,
                                             self.level+1))
            return (submarkets, total_properties)
        return (None, total_properties)


    def crawl_market(self, max_prop_visit, num_properties_visited=0):
        '''
        Recursive function that takes a market, a max number of properties to
        visit and a number of properties visited so far and asigns crawler
        objects to the markets without submarkets and crawls those markets.
        Returns list of dictionaries of properties and the number of properties
        visited in this crawl + the number of properties
        previously visited.

        Inputs:
            max_prop_visit: int
            num_properties_visited: int
        Output:
            (list of dictionaries, int)
        '''
        start_time = time.time()
        if max_prop_visit == 0:
            return([], 0)

        if not self.submarkets:
            self.crawler = Crawler(self.market_url, self.type_of_offer,
                                   self.type_of_prop, max_prop_visit,
                                   num_properties_visited)
            if max_prop_visit > num_properties_visited:
                start_time = time.time()
                self.crawler.crawl()
                print("Mkt crawled in {} secs"
                      .format(round(time.time() - start_time, 2)))
                return (self.crawler.properties_info,
                        self.crawler.num_properties_visited)

        total_prop_info = []
        for submarket in self.submarkets:
            properties_info, new_num_properties_visited =\
                            submarket.crawl_market(max_prop_visit, num_properties_visited)
            num_properties_visited = new_num_properties_visited
            total_prop_info += properties_info

        return (total_prop_info, num_properties_visited)


    def print(self, prefix='--'):
        '''
        print Market structure
        '''
        print(prefix * self.level + self.label +
              ' : {}'.format(self.num_props))
        for submarket in self.submarkets:
            submarket.print()


class Crawler:
    '''
    Class to represent a crawler of a market.
    '''

    def __init__(self, market_url, type_of_offer, type_of_prop,
                 max_prop_visit, num_properties_visited):
        '''
        Initializer of the Crawler class with the initial market url and the
        max number of properties to scrape.
        Inputs:
            initial_market_url: str
            max_prop_visit: int
        '''
        self.market_url = market_url
        self.max_prop_visit = max_prop_visit
        self.num_properties_visited = num_properties_visited
        self.type_of_offer = type_of_offer
        self.type_of_prop = type_of_prop
        self.market_urls_seen = set([market_url])
        self.market_pages_to_visit = queue.Queue()
        self.market_pages_to_visit.put(self.market_url)
        self.market_pages_visited = []
        self.properties_scrapped_url = []
        self.properties_info = []


    def update_market_pages(self, market_soup):
        '''
        Returns  the urls of all the market pages linked in the  market
        webpage represented by the soup, and updates the list of
        market pages seen and appends to the queue of market pages to visit.
        Returns True if new market was seen.
        Inputs:
            soup_market: BS4 object that represents a market page.
        Output:
            Bool
        '''
        market_pages_links = market_soup\
                             .find_all('a', class_="andes-pagination__link")\
                             [2:-1]
        new_market_seen = False
        for market_tag in market_pages_links:
            market_url = market_tag['href']
            if not market_url in self.market_urls_seen:
                new_market_seen = True
                self.market_pages_to_visit.put(market_url)
                self.market_urls_seen.add(market_url)
        return new_market_seen


    def get_property_characs(self, prop_url):
        '''
        Get property characteristics from prop url.
        Inputs:
            prop_soup:string
            prop_url: string
        Output:
            Dict
        '''
        if prop_url in self.properties_scrapped_url:
            return False
        prop_soup = get_soup(prop_url)
        if not prop_soup:
            return False
        prop_info = {'url':prop_url,
                     'type_of_offer' : self.type_of_offer,
                     'type_of_prop' : self.type_of_prop}

        get_basic_info(prop_soup, prop_info)
        get_location_info(prop_soup, prop_info)
        get_characs(prop_soup, prop_info)
        get_location(prop_soup, prop_info)
        get_description(prop_soup, prop_info)
        get_extras(prop_soup, prop_info)
        if (("Recámaras" not in prop_info) or
                ("Baños" not in prop_info) or
                ("Superficie construida" not in prop_info)):
            get_vip_attributes(prop_soup, prop_info)

        self.properties_info.append(prop_info)
        self.properties_scrapped_url.append(prop_url)
        self.num_properties_visited += 1
        print(self.num_properties_visited)

        return True


    def clean_crawler(self):
        '''
        reset crawler to factory config.
        '''
        self.market_urls_seen = set([self.market_url])
        self.market_pages_to_visit = queue.Queue()
        self.market_pages_to_visit.put(self.market_url)
        self.market_pages_visited = []
        self.properties_scrapped_url = []
        self.properties_info = []


    def crawl(self):
        '''
        crawl the marketplace. For each of the marketpages in the
        market, optaing the information of each of the properties
        and returns a list of all the properties scrapped.

        Indirect Output:
            Updates: self.market_pages_visited
                     self.properties_scrapped
                     self.properties_info

        Direct output:
            List of dicts
        '''
        market_url = self.market_pages_to_visit.get()
        market_soup = get_soup(market_url)
        
        if market_soup:
            start_mkt_page_time = time.time()
            properties_links = get_properties_links(market_soup)
            print("Getting properties from market page {}".format(market_url))
            for property_link in properties_links:
                if self.num_properties_visited >= self.max_prop_visit:
                    break
                start_prop_time = time.time()
                self.get_property_characs(property_link)
                print("property scrapped in {} secs"
                      .format(round(time.time() - start_prop_time, 2)))
            self.market_pages_visited.append(market_url)
            self.update_market_pages(market_soup)
            print()
            print("Mkt page crawled in {} secs"
                  .format(round(time.time() - start_mkt_page_time, 2)))
        if (not self.market_pages_to_visit.empty() and
                self.num_properties_visited < self.max_prop_visit):
            self.crawl()
        return self.properties_info


    def __repr__(self):
        '''
        Representation method
        '''
        return "Crawler of {}".format(self.market_url)


def get_total_results(market_soup):
    '''
    Get the total results that are in the market.
    Inputs:
        market soup: Beautiful Soup.
    Output:
        int
    '''
    results_str = market_soup.find('span', class_="ui-search-search-result__quantity-results")
    #print(f'***************** {results_str}')
    if results_str:
        results_str = results_str.text
        results_str = re.search(r'[0-9,]+', results_str).group()
        return int(('').join(results_str.split(',')))
    return None


def get_properties_links(market_soup):
    '''
    Returns the urls of all the properties announced in the market
    webpage represented by the soup.
    Inputs:
        soup_market: BS4 object that represents a market page.
    Output:
        List of str
    '''
    properties_links = market_soup.find_all('a', class_="ui-search-result__content ui-search-link")
    #print(f'----- {properties_links}')
    return [tag['href'] for tag in properties_links]


def get_basic_info(prop_soup, prop_info):
    '''
    Get basic information from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''
    prop_basic = prop_soup.find('script', attrs={"type":"application/ld+json"})
    if prop_basic:
        prop_basic = prop_basic.text
        prop_basic = re.search(r'\{.*\}', prop_basic)
        prop_basic = ast.literal_eval(prop_basic.group())
        prop_info['name'] = prop_basic['name']
        prop_info['price'] = int(prop_basic['offers']['price'])
        prop_info['currency'] = prop_basic['offers']['priceCurrency']
        
def get_location_info(prop_soup, prop_info):
    '''
    Get basic information from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''
    prop_basic = prop_soup.findAll('script', attrs={"type":"application/ld+json"})
    if prop_basic:
        prop_basic = prop_basic[1].text
        #print(f'= GET LOCATION ======== {prop_basic}')
        prop_basic = re.search(r'\{.*\}', prop_basic)
        prop_basic = ast.literal_eval(prop_basic.group())
        
        itemElements = prop_basic['itemListElement']
        #print(f'----- {itemElements}')
        for x in itemElements:
            if x['position'] == 4:
                prop_info['Estado'] = x['item']['name']
            if x['position'] == 5:
                prop_info['Ciudad'] = x['item']['name']
            if x['position'] == 6:
                prop_info['Colonia'] = x['item']['name']

def get_characs(prop_soup, prop_info):
    '''
    Get characs from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''

    prop_characs = prop_soup.find_all('tr', class_="andes-table__row")

    for charac in prop_characs:
        charac_title = charac.find('th', class_="ui-pdp-specs__table__column-title").text
        charac_title = charac_title.replace('\u00e1','a').replace('\u00fc','u').replace('\u00f1','n')
        charac_value = charac.find('span', class_="andes-table__column--value").text
        if re.search(r'\d', charac_value):
            charac_value = float(re.search(r'[0-9.]+', charac_value).group())
        prop_info[charac_title] = charac_value


def get_location(prop_soup, prop_info):
    '''
    Get location from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''

    prop_location = prop_soup.find_all('script', attrs=
                                       {"type":"text/javascript"})
    if prop_location:
        prop_location = prop_location[-1].text
        longitude = re.search(r'longitude:.[0-9-.]+', prop_location)
        if longitude:
            longitude = longitude.group()
            longitude = re.search(r'[0-9-.]+', longitude).group()
            prop_info['longitude'] = longitude
        latitude = re.search('latitude:.[0-9-.]+', prop_location)
        if latitude:
            latitude = latitude.group()
            latitude = re.search(r'[0-9-.]+', latitude).group()
            prop_info['latitude'] = latitude


def get_description(prop_soup, prop_info):
    '''
    Get description from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''
    prop_description = prop_soup.find('pre', class_="preformated-text")
    if prop_description:
        prop_description = prop_description.text
        prop_info['description'] = prop_description


def get_extras(prop_soup, prop_info):
    '''
    Get extras from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''
    prop_extras_groups = prop_soup.find_all('ul', class_=
                                            "boolean-attribute-list")
    for group in prop_extras_groups:
        extra_characs = group.find_all('li')
        for charac in extra_characs:
            prop_info[charac.text] = True


def get_vip_attributes(prop_soup, prop_info):
    '''
    Get extras from a property soup and update the property info
    dictionary.
    Inputs:
        prop_soup: Beautiful Soup
        prop_info: dict
    Indirect Output: Modifies dictionary
    '''
    vip_attributes = prop_soup.find_all('li', class_=
                                        "vip-product-info__attribute_element")
    for attribute in vip_attributes:
        attribute_name = attribute.find('p').text
        vip_value = attribute.find('span',
                                   class_="vip-product-info__attribute-value")\
                                   .text
        if "-" in vip_value:
            attribute_values = [float(x) for x in vip_value.split(" - ")]
            attribute_average = sum(attribute_values) / len(attribute_values)
        else:
            attribute_average = float(re.search(r'[0-9.]+', vip_value).group())
        if attribute_name == 'm² construidos':
            attribute_name = "Superficie construida"
        prop_info[attribute_name] = attribute_average


def go(state, type_of_offer, type_of_prop, output_json_file,
       max_prop_visit=float('inf')):
    '''
    Function to crawl the entire market. Writes the resul to the json file
    Inputs:
        Inputs:
            state: ('Distrito  Federal' or 'Estado de Mexico') str 
            type_of_offer: ('sale' or 'rent') str
            type_of_prop: ('houses' or 'apartments') str
            output_json_file: str
            max_prop_visit: int
        Outputs:
            (list of dicts, int)
    '''
    start_time = time.time()
    mkt = Market(state, type_of_offer, type_of_prop)
    prop_info, num_properties_scrapped = mkt.crawl_market(max_prop_visit)

    with open(output_json_file, 'w') as fp:
        json.dump(prop_info, fp)
    print("Total time: {} seconds".format(round(time.time() - start_time)))

    return (prop_info, num_properties_scrapped)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('Please specify State, type of offer, type of prop and Output file')
    elif len(sys.argv) == 5:
        go(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        go(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
            int(sys.argv[5]))
    
