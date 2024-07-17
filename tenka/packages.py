import requests

from .main import PackageManager

def get_branches(repo_name: str):
    url = f"https://api.github.com/repos/{repo_name}/branches"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch branches")

def search_package(package_name: str, manager: PackageManager):
    url = f"https://api.github.com/search/repositories?q={package_name}+language:mojo"
    response = requests.get(url)
    if response.status_code == 200:
        search_results =  response.json()['items']
        print(f"Package {package_name} found successfully at {search_results[0]['html_url']}")
    else:
        raise Exception("Failed to search GitHub")

    press = input("Do you want to install this package? (y/n): ")

    if press == "y":
        manager.install_package(package_name)
    else: 
        quit() 

def get_packages():
    pass

def install_package(package_name: str):
    pass    

def delete_package(packages):
    pass

def update_package(packages):
    pass