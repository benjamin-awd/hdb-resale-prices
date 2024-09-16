from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import pandas as pd
import requests
import streamlit as st
from tqdm import tqdm


@lru_cache
def extract_hdb_data(year_month):
    data = {
        "filters": f'{{"month":"{year_month}"}}',
        "limit": "14000",
    }
    search_url = "https://data.gov.sg/api/action/datastore_search?resource_id=d_8b84c4ee58e3cfc0ece0d773c8ca6abc"

    response = requests.request("GET", search_url, params=data)
    return response.json()["result"]["records"]


def get_data():
    start_date = "2024-07"
    end_date = pd.Timestamp.now().strftime("%Y-%m")
    dates = (
        pd.date_range(start=start_date, end=end_date, freq="MS")
        .strftime("%Y-%m")
        .tolist()
    )

    responses = []
    for date in dates:
        res = extract_hdb_data(date)
        responses.append(res)

    all_items = [item for res in responses for item in res]
    df = pd.DataFrame(all_items)
    df["address"] = df[["block", "street_name"]].apply(lambda x: " ".join(x), axis=1)
    df = df.reset_index().drop("index", axis=1)
    return df


def fetch_map_data(query_address, session: requests.Session):
    query_string = (
        f"https://www.onemap.gov.sg/api/common/elastic/search?&searchVal="
        + str(query_address)
        + "&returnGeom=Y&getAddrDetails=Y"
    )

    response = session.get(query_string).json()["results"][0]

    return {
        "address": query_address,
        "postal": response["POSTAL"],
        "latitude": response["LATITUDE"],
        "longitude": response["LONGITUDE"],
    }


def get_map_results(data):
    unique_address = list(dict.fromkeys(data["address"]))
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(
                tqdm(
                    executor.map(
                        lambda addr: fetch_map_data(addr, session), unique_address
                    ),
                    total=len(unique_address),
                )
            )

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = get_data()
    print("Total number of observations: {}".format(df.shape[0]))
    map_data = get_map_results(df)

    final_data = df.merge(map_data, how="left", on="address")
    print("Total number of observations after merging: {}".format(final_data.shape[0]))
    final_data.to_csv("data.csv")
