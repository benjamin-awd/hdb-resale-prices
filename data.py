import requests
import datetime
import pandas as pd
import json
from tqdm import tqdm

def get_data(api_url):
    # Get data using API
    response = requests.get(api_url)
    data_items = response.json()["result"]["records"]
    
    all_data = []
    for item in data_items:
        data = {'month': item["month"],
                'town': item["town"],
                'flat_type': item["flat_type"],
                'block': item["block"],
                'street_name': item["street_name"],
                'storey_range': item["storey_range"],
                'floor_area_sqm': item["floor_area_sqm"],
                'flat_model': item["flat_model"],
                'lease_commence_date': item["lease_commence_date"],
                'remaining_lease': item["remaining_lease"],
                'resale_price': item["resale_price"]}
        all_data.append(data)
        
    full_data =  pd.DataFrame(all_data)
    
    # Filter to get past one year data only
    today = datetime.datetime.today()
    date_range = [today - datetime.timedelta(days=x) for x in range(365)]

    date_list = []
    for date in date_range:
        date_format = date.strftime("%Y-%m")
        if date_format not in date_list:
            date_list.append(date_format)
            
    data = full_data[full_data["month"].isin(date_list)]
    data["address"] = data[['block', 'street_name']].apply(lambda x: ' '.join(x), axis=1)
    data = data.reset_index().drop("index",axis=1)
    return data
    
def get_map_results(data):
    
    all_map_data = []
    unique_address = list(dict.fromkeys(data["address"]))
    for i in tqdm(range(0, len(unique_address))):
        query_address = unique_address[i]
        query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(query_address) + '&returnGeom=Y&getAddrDetails=Y'
        response = requests.get(query_string).json()["results"][0]
        map_data = {'address': query_address,
                    'postal': response["POSTAL"],
                    'latitude': response["LATITUDE"],
                    'longitude': response["LONGITUDE"]}
        all_map_data.append(map_data)
    
    
    return pd.DataFrame(all_map_data)
        

if __name__ == "__main__":
    # Get data
    api_url = 'https://data.gov.sg/api/action/datastore_search?resource_id=f1765b54-a209-4718-8d38-a39237f502b3&limit=1000000'
    data = get_data(api_url)
    print("Total number of observations: {}".format(data.shape[0]))
    map_data = get_map_results(data)
    
    # merge
    final_data = data.merge(map_data, how="left", on="address")
    print("Total number of observations after merging: {}".format(final_data.shape[0]))
    final_data.to_csv("data.csv")
    

