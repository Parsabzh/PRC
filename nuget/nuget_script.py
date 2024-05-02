import requests
import json
import pandas as pd
import os
import logging
from package import Package

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
with open('config.json') as json_file:
    config = json.load(json_file)

nuget_catalog_url = config.get("api_urls", {}).get("nuget_catalog_url", "")

def fetch_json_response_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JSON response from URL {url}: {e}")
        return {}

def fetch_package_data(item):
    package_url = item.get("@id", "")
    package_id = item.get("nuget:id", "")
    package_version = item.get("nuget:version", "")
    package_data = fetch_json_response_from_url(package_url)
    package_des = package_data.get("description", "")
    package_author = package_data.get("authors", "")
    return Package(url=package_url, package_id=package_id, version=package_version, description=package_des, author=package_author)

def save_data(data, filename):
    serializable_data = [item.to_dict() for item in data if isinstance(item, Package)]
    with open(filename, 'w') as f:
        json.dump(serializable_data, f, indent=4)

def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load data from {filename}: {e}")
    return []

def process_catalog_data(catalog_url, save_interval=1000, save_filename="processed_data.json"):
    try:
        package_data_list = load_data(save_filename)
        package_count = len(package_data_list)

        catalog_data = fetch_json_response_from_url(catalog_url)
        items = catalog_data.get("items", [])

        package_data_list = process_catalog_items(items, package_count, package_data_list, save_interval, save_filename)

        save_data(package_data_list, save_filename)

        return package_data_list
    except Exception as e:
        logger.error(f"An error occurred while processing catalog data: {e}")
        return []

def process_catalog_items(items, package_count, package_data_list, save_interval, save_filename):
    for item in items:
        try:
            page_url = item.get("@id", "")
            page_data = fetch_json_response_from_url(page_url)
            page_items = page_data.get("items", [])

            package_data_list, package_count = process_page_items(page_items, package_count, package_data_list, save_interval, save_filename)
        except Exception as e:
            logger.error(f"An error occurred while processing catalog items: {e}")

    return package_data_list

def process_page_items(page_items, package_count, package_data_list, save_interval, save_filename):
    for page_item in page_items:
        try:
            package_count += 1
            package = fetch_package_data(page_item)
            package_data_list.append(package)

            if package_count % save_interval == 0:
                save_data(package_data_list, save_filename)
                logger.info(f"Processed {package_count} packages. Data saved.")
        except Exception as e:
            logger.error(f"An error occurred while processing page items: {e}")

    return package_data_list, package_count

def fetch_nuget_packages():
    try:
        package_data_list = process_catalog_data(nuget_catalog_url)

        df = pd.DataFrame([item.to_dict() for item in package_data_list if isinstance(item, Package)])
        df.to_csv("nuget_package_data.csv", index=False)
    except Exception as e:
        logger.error(f"An error occurred while fetching NuGet packages: {e}")

