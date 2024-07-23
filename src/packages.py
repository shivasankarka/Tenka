import requests

def get_branches(repo_name: str):
    url = f"https://api.github.com/repos/{repo_name}/branches"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch branches")

def get_packages():
    pass

def install_package(package_name: str):
    pass    

def delete_package(packages):
    pass

def update_package(packages):
    pass