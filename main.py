import requests
import pandas as pd
import json
import csv
from package import Package


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


def process_catalog_data(catalog_url):
    catalog_data = fetch_json_response_from_url(catalog_url)
    items = catalog_data.get("items", [])
    package_data_list = []
    package_count = 0
    for item in items:
        page_url = item.get("@id", "")
        page_data = fetch_json_response_from_url(page_url)
        page_items = page_data.get("items", [])
        for page_item in page_items:
            package_count += 1  # Increment counter for each package processed
            package = fetch_package_data(page_item)
            package_data_list.append(package)
            print(f"Processed {package_count} packages")
    return package_data_list

def main():
    package_data_list = process_catalog_data(nuget_catalog_url)

    df = pd.DataFrame(package_data_list)
    df.to_csv("nuget_package_data.csv", index=False)

if __name__ == "__main__":
    main()


