import requests
from package import Package
import json
import pandas as pd
import os

with open('config.json') as json_file:
    config = json.load(json_file)

def fetch_json_response_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching JSON from URL {url}: {e}")
        return None

pip_package_names_url = config["api_urls"]["pip_package_names_url"]
pip_package_data_url = config["api_urls"]["pip_package_data_url"]
save_filename = config.get("save_filename", "pip_package_data.json")

def save_data(data, filename):
    serializable_data = [item.to_dict() for item in data if isinstance(item, Package)]

    with open(filename, 'w') as f:
        json.dump(serializable_data, f, indent=4)

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def process_package_data(item):
    package_info = item.get("info", {})
    package_url = package_info.get("release_url", "")
    package_id = package_info.get("name", "")
    package_version = package_info.get("version", "")
    package_des = package_info.get("summary", "")
    package_author = package_info.get("author", "")
    return Package(url=package_url, package_id=package_id, version=package_version, description=package_des, author=package_author)

def get_package_info(package_name):
    url = pip_package_data_url.format(package_name)
    package_data = fetch_json_response_from_url(url)
    if package_data:
        return process_package_data(package_data)
    return None

def get_all_package_names():  
    packages = fetch_json_response_from_url(pip_package_names_url)
    if packages:
        return [package[0] for package in packages]
    return []

def fetch_pip_packages():
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
    df.to_csv("pip_package_data.csv", index=False)

