import requests
import json
from nuget.package import Package
import pandas as pd
import json
import os

with open('config.json') as json_file:
    data = json.load(json_file)

nuget_catalog_url = data["api_urls"]["nuget_catalog_url"]

    
def fetch_json_response_from_url(url):
    response = requests.get(url)
    return response.json()

def fetch_package_data(item):
    package_url = item.get("@id", "")
    package_id = item.get("nuget:id", "")
    package_version = item.get("nuget:version", "")
    package_data = fetch_json_response_from_url(package_url)
    package_des = package_data.get("description", "")
    package_author = package_data.get("authors", "")
    return Package(url=package_url, package_id=package_id, version=package_version, description=package_des, author=package_author)

def save_data(data, filename):
    serializable_data = []

    for item in data:
        if isinstance(item, Package):
            serializable_data.append(item.to_dict())

    with open(filename, 'w') as f:
        json.dump(serializable_data, f, indent=4)

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def process_catalog_data(catalog_url, save_interval=1000, save_filename="processed_data.json"):
    package_data_list = load_data(save_filename)
    package_count = len(package_data_list)

    catalog_data = fetch_json_response_from_url(catalog_url)
    items = catalog_data.get("items", [])

    for item in items:
        page_url = item.get("@id", "")
        page_data = fetch_json_response_from_url(page_url)
        page_items = page_data.get("items", [])

        for page_item in page_items:
            package_count += 1
            package = fetch_package_data(page_item)
            package_data_list.append(package)

            if package_count % save_interval == 0:
                save_data(package_data_list, save_filename)
                print(f"Processed {package_count} packages. Data saved.")

    save_data(package_data_list, save_filename)

    return package_data_list


def fetch_nuget_packages():
    package_data_list = process_catalog_data(nuget_catalog_url)

    df = pd.DataFrame(package_data_list)
    df.to_csv("nuget_package_data.csv", index=False)