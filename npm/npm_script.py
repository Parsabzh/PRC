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

npm_package_search_url = config.get("api_urls", {}).get("npm_package_search_url", "")
npm_package_names_url = config.get("api_urls", {}).get("npm_package_names_url", "")
save_filename = config.get("save_filename", "npm_package_data.json")


def fetch_json_response_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JSON response from URL {url}: {e}")
        return {}
    
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


def process_package_data(item):
    package_name = item.get("package", {}).get("name", "").replace("-", "")
    package_version = item.get("package", {}).get("version", "")
    package_url = item.get("package", {}).get("links", {}).get("npm", "")
    package_description = item.get("package", {}).get("description", "")
    package_author = item.get("package", {}).get("author", {}).get("name", "")

    return Package(
        name=package_name,
        version=package_version,
        url=package_url,
        author=package_author,
        description=package_description
    )

def get_package_info(package_name):
    url = npm_package_search_url.format(package_name)
    package_data = fetch_json_response_from_url(url)
    if package_data:
        return process_package_data(package_data)
    return None

def get_all_package_names():  
    packages = fetch_json_response_from_url(npm_package_names_url)
    if packages:
        return [package[0] for package in packages]
    return []

def fetch_npm_packages():
    existing_data = load_data(save_filename)
    package_data_list = existing_data if existing_data else []

    package_names = get_all_package_names()

    for package_name in package_names:
        if any(package.package_id == package_name for package in package_data_list):
            print(f"Skipping package '{package_name}'. Already processed.")
            continue

        package = get_package_info(package_name)
        if package:
            package_data_list.append(package)
        
    save_data(package_data_list, save_filename)

    df = pd.DataFrame(package_data_list)
    df.to_csv("npm_package_data.csv", index=False)