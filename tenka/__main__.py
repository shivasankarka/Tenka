import os
import requests
import shutil
import subprocess
import argparse
import datetime
import json

class PackageManager:
    def __init__(self, home_directory):
        self.home_directory = os.getenv('MODULAR_HOME', os.path.expanduser('~/.modular'))
        self.home_directory = os.path.join(self.home_directory, "pkg", "packages.modular.com_mojo", "lib", "mojo")
        if not os.path.exists(self.home_directory):
            os.makedirs(self.home_directory)
        subprocess.run(f"export MOJO_INCLUDE_PATH={self.home_directory}", shell=True, check=True)

    def search(self, package_name):
        url = f"https://api.github.com/search/repositories?q={package_name}+language:mojo"
        response = requests.get(url)
        if response.status_code == 200:
            search_results =  response.json()['items']
            print(f"Package {package_name} found successfully at {search_results[0]['html_url']}")
        else:
            raise Exception("Failed to search GitHub")
    
        press = input("Do you want to install this package? (y/n): ")
        if press == "y":
            self.install_package(package_name)
        else: 
            quit()

    def search_github(self, package_name):
        url = f"https://api.github.com/search/repositories?q={package_name}+language:mojo"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['items']
        else:
            raise Exception("Failed to search GitHub")

    def get_branches(self, repo_full_name):
        url = f"https://api.github.com/repos/{repo_full_name}/branches"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch branches")

    def download_package(self, repo_url, package_name, branch='main'):
        download_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            package_path = os.path.join(self.home_directory, f"{package_name}.zip")
            with open(package_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return package_path
        else:
            raise Exception("Failed to download package")

    def install_package(self, package_name, branch=False):
        search_results = self.search_github(package_name)
        if search_results:
            repo = search_results[0]
            repo_url = repo['html_url']
            repo_full_name = repo['full_name']
            
            branches = self.get_branches(repo_full_name)
            if branch is True and len(branches) > 1:
                print("Available branches:")
                for i, branch in enumerate(branches, 1):
                    print(f"{i}. {branch['name']}")
                while True:
                    choice = input("Choose a branch number (or press Enter for main): ")
                    if choice == "":
                        branch = 'main'
                        break
                    try:
                        branch_index = int(choice) - 1
                        if 0 <= branch_index < len(branches):
                            branch = branches[branch_index]['name']
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            else:
                branch = 'main'
            
            package_path = self.download_package(repo_url, package_name, branch)
            shutil.unpack_archive(package_path, self.home_directory)
            os.remove(package_path)
            package_directory = os.path.join(self.home_directory, f"{package_name}-{branch}".lower())
            
            try:
                print(package_directory)
                os.chdir(package_directory)
                if os.path.exists(package_name + ".mojopkg"):
                    print(f"Package {package_name} found successfully.")
                    mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                    shutil.move(mojopkg_path, self.home_directory)
                    print(f"Package {package_name}.mojopkg moved to {self.home_directory}")
                    
                else:
                    if os.path.exists(package_name):
                        result = subprocess.run(["mojo", "package", package_name], check=True, capture_output=True, text=True)
                    else:
                        result = subprocess.run(["mojo", "package", "src"], check=True, capture_output=True, text=True)
                    print(f"Package {package_name} packaged successfully.")
                    print(result.stdout)
                
                    # moves the .mojopkg file to the home directory
                    # mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                    # shutil.move(mojopkg_path, self.home_directory)
                    # print(f"Package {package_name}.mojopkg moved to {self.home_directory}")
    
                # deletes the package directory
                # shutil.rmtree(package_directory)
                # print(f"Package directory {package_directory} deleted")
                if not os.path.exists(os.path.join(self.home_directory, f"{package_name}".lower())):
                    os.rename(os.path.join(self.home_directory, f"{package_name}-{branch}".lower()), os.path.join(self.home_directory, f"{package_name}".lower()))
                
                # Create or update the JSON file with package information
                json_file_path = os.path.join(self.home_directory, 'installed_packages.json')
                package_info = {
                    'name': package_name,
                    'branch': branch,
                    'install_date': datetime.datetime.now().date().isoformat()
                }
                
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as f:
                        if f.read().strip():
                            f.seek(0)  # reset file pointer to beginning
                            installed_packages = json.load(f)
                        else:
                            installed_packages = []
                            
                    # Check if package already exists
                    for i, pkg in enumerate(installed_packages):
                        if pkg['name'] == package_name:
                            # Overwrite existing package info
                            installed_packages[i] = package_info
                            break
                    else:
                        installed_packages.append(package_info)
                else:
                    installed_packages = [package_info]
                
                with open(json_file_path, 'w') as f:
                    json.dump(installed_packages, f, indent=4)
                
                print(f"Package information saved to {json_file_path}")
                
            except subprocess.CalledProcessError as e:
                print(f"Failed to package {package_name}.")
                print(e.stderr)   
        else:
            print(f"No package found for {package_name}")
        
    def remove_package(self, package_name):
        try:
            if (os.path.exists(os.path.join(self.home_directory, f"{package_name}.mojopkg"))):
                os.remove(os.path.join(self.home_directory, f"{package_name}.mojopkg"))
                
            if (os.path.exists(os.path.join(self.home_directory, f"{package_name}".lower()))):
                shutil.rmtree(os.path.join(self.home_directory, f"{package_name}".lower()))
            
            json_file_path = os.path.join(self.home_directory, 'installed_packages.json') 
            with open(json_file_path, 'r') as f:
                if f.read().strip():
                    f.seek(0)  # reset file pointer to beginning
                    installed_packages = json.load(f)
                else:
                    installed_packages = []
                        
            for i, pkg in enumerate(installed_packages):
                if pkg['name'] == package_name:
                    del installed_packages[i]
                    break
                
            print(f"Package {package_name} removed successfully.")

        except FileNotFoundError as e:
            raise (f"Package {package_name} not found.")

    def create(self, package_name):
        base_dir = os.path.expanduser("~/.modular_envs")
        env_dir = os.path.join(base_dir, env_name)
    
        if os.path.exists(env_dir):
            print(f"Environment '{env_name}' already exists.")
            return
    
        os.makedirs(env_dir)
        # Copy the base Mojo environment to the new environment directory
        base_mojo_env = os.path.expanduser("~/.modular")
        shutil.copytree(base_mojo_env, os.path.join(env_dir, ".modular"))
        
        print(f"Environment '{env_name}' created successfully at {env_dir}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: create_env.py <env_name>")
    else:
        create_env(sys.argv[1])
            
def main():
    parser = argparse.ArgumentParser(description="Package Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # create the parser for the "install" command
    parser_install = subparsers.add_parser('install', help='install help')
    parser_install.add_argument("package_name", help="Name of the package to install")
    parser_install.add_argument("--branch", action='store_true', help="Search for branches")

    # create the parser for the "search" command
    parser_search = subparsers.add_parser('search', help='search help')
    parser_search.add_argument("package_name", help="Name of the package to search")

    # create the parser for the "remove" command
    parser_remove = subparsers.add_parser('remove', help='remove help')
    parser_remove.add_argument("package_name", help="Name of the package to remove")

    args = parser.parse_args()

    manager = PackageManager(home_directory="packages")

    if args.command == "install":
        manager.install_package(args.package_name, branch=args.branch)
    elif args.command == "search":
        manager.search(args.package_name)
    elif args.command == "remove":
        manager.remove_package(args.package_name)

if __name__ == "__main__":
    main()