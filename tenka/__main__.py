import os
import requests
import shutil
import subprocess
import argparse
import datetime
import json

class PackageManager:
    def __init__(self):
        self.home_directory = os.path.expanduser("~/.modular/pkg/packages.modular.com_mojo/lib")
        if not os.path.exists(os.path.join(self.home_directory, "base")):
            try:
                shutil.copytree(self.home_directory+"/mojo/", self.home_directory+"/base/")
            except shutil.Error as e:
                print(f"Error copying files: {e}")
                shutil.rmtree(self.home_directory+"/base")
                return

        if not os.path.exists(os.path.join(os.path.expanduser("~/.modular"), 'active.json')):
            json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w') as file:
                json.dump({"active_environment": "base"}, file, indent=4)
            
        if not os.path.exists(os.path.join(os.path.expanduser("~/.modular"), 'environments.json')):
            envs_json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'environments.json')
            environment_info = {
                'name': "base",
                'created_date': datetime.datetime.now().date().isoformat(),
                'packages': []
            }
            with open(envs_json_file_path, 'w') as file:
                json.dump([environment_info], file, indent=4)

    def search_package(self, package_name):
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
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'r') as file:
            temp = json.load(file)
        active_env = temp['active_environment']
        print("active_env: ", active_env)
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
            branch_path = os.path.join(self.home_directory, active_env)
            shutil.unpack_archive(package_path, branch_path)
            os.remove(package_path)
            package_directory = os.path.join(branch_path, f"{package_name}-{branch}".lower())
            print("package_directory: ", package_directory)
            print("package_name: ", package_name)
            print("branch path: ", branch_path)
            try:
                os.chdir(package_directory)
                if os.path.exists(package_name + ".mojopkg"):
                    print(f"Package {package_name} found successfully.")
                    mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                    shutil.move(mojopkg_path, branch_path)
                    print(f"Package {package_name}.mojopkg moved to {self.home_directory}")
                elif os.path.exists(''.join(e for e in package_name if e.isalnum()) + ".mojopkg"):
                    new_package_name = ''.join(e for e in package_name if e.isalnum())
                    print(f"Package {new_package_name} found successfully.")
                    mojopkg_path = os.path.join(package_directory, f"{new_package_name}.mojopkg")
                    shutil.move(mojopkg_path, branch_path)
                    print(f"Package {new_package_name}.mojopkg moved to {self.home_directory}") 
                else:
                    if os.path.exists(package_name):
                        result = subprocess.run(["mojo", "package", package_name], check=True, capture_output=True, text=True)
                    elif os.path.exists("src"):
                        result = subprocess.run(["mojo", "package", "src"], check=True, capture_output=True, text=True)
                    else:
                        for folder in os.listdir(package_directory):
                            if folder.lower() in package_name.lower():
                                subprocess.run(["mojo", "package", folder], check=True, capture_output=True, text=True)
                                break
                    print(f"Package {package_name} packaged successfully.")
                    # print(result.stdout)
                
                    # # moves the .mojopkg file to the home directory
                    try:
                        mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                        shutil.move(mojopkg_path, branch_path)
                        print(f"Package {package_name}.mojopkg moved to {branch_path}")
                    except FileNotFoundError as e:
                        print(f"Package {package_name}.mojopkg not found. {e}")

                # deletes the package directory
                package_folder = os.path.join(package_directory, f"{package_name}".lower())
                if os.path.exists(package_folder):
                    shutil.move(package_folder, branch_path)
                else:
                    for folder in os.listdir(package_directory):
                        if folder.lower() in package_name.lower():
                            shutil.move(os.path.join(package_directory, folder), branch_path)
                            break
                    
                shutil.rmtree(package_directory)
                print(f"Package directory {package_directory} deleted")

                # Create or update the JSON file with package information
                json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'environments.json')
                package_info = {
                    'name': package_name,
                    'branch': branch,
                    'install_date': datetime.datetime.now().date().isoformat()
                }
                
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r') as f:
                        installed_packages = json.load(f)
                        # Check if the active environment exists
                        env_found = False
                        for env in installed_packages:
                            if env['name'] == active_env:
                                env_found = True
                                # Check if the package already exists in the environment
                                package_exists = False
                                for package in env['packages']:
                                    if package['name'] == package_name:
                                        package_exists = True
                                        break
                                if not package_exists:
                                    env['packages'].append(package_info)
                                break
                        if not env_found:
                            # If the active environment does not exist, add it with the package
                            installed_packages.append({
                                'name': active_env,
                                'created_date': datetime.datetime.now().date().isoformat(),
                                'packages': [package_info]
                            })
                
                with open(json_file_path, 'w') as f:
                    json.dump(installed_packages, f, indent=4)
                
                print(f"Package information saved to {json_file_path}")
                
            except subprocess.CalledProcessError as e:
                print(f"Failed to package {package_name}.")
                print(e.stderr)   
        else:
            print(f"No package found for {package_name}")
        
    def remove(self, env_name):
        shutil.rmtree(os.path.join(self.home_directory, env_name))
        json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'environments.json')
        with open(json_file_path, 'r') as f:
            if f.read().strip():
                f.seek(0)
                environments = json.load(f)
            else:
                environments = []
                
        for i, env in enumerate(environments):
            if env['name'] == env_name:
                del environments[i]
                break
            
        with open(json_file_path, 'w') as f:
            json.dump(environments, f, indent=4)
        
        print(f"Environment {env_name} removed successfully.")

    def create(self, env_name):
        if env_name == "base":
            print("Cannot create an environment with the name 'base'.")
            return
        base_dir = os.path.expanduser("~/.modular/pkg/packages.modular.com_mojo/lib")
        env_dir = os.path.join(base_dir, env_name)
        
        if not os.path.exists(os.path.join(self.home_directory, env_name)):
            try:
                shutil.copytree(self.home_directory+"/mojo/",os.path.join(self.home_directory, env_name))
            except shutil.Error as e:
                print(f"Error copying files: {e}")
                shutil.rmtree(self.home_directory+"/base")
                return 
        else:
            print(f"Environment '{env_name}' already exists.")
            return
            
        print(f"Environment '{env_name}' created successfully at {env_dir}.")
        
        # Create or update the JSON file with environment information
        json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'environments.json')
        environment_info = {
            'name': env_name,
            'created_date': datetime.datetime.now().date().isoformat(),
            'packages': []
        }
        
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                if f.read().strip():
                    f.seek(0)  # reset file pointer to beginning
                    environments = json.load(f)
                else:
                    environments = []
                    
            # Check if environment already exists
            for i, env in enumerate(environments):
                if env['name'] == env_name:
                    print("Environment already exists.")
                    break
            else:
                environments.append(environment_info)
        else:
            environments = [environment_info]
        
        with open(json_file_path, 'w') as f:
            json.dump(environments, f, indent=4)
        
        print(f"Environment information saved to {json_file_path}")

    def uninstall(self, package_name):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'r') as file:
            temp = json.load(file)
        active_env = temp['active_environment']
        package_dir = os.path.join(self.home_directory, active_env)
        try:
            if (os.path.exists(os.path.join(package_dir, f"{package_name}.mojopkg"))):
                os.remove(os.path.join(package_dir, f"{package_name}.mojopkg"))
                
            if (os.path.exists(os.path.join(package_dir, f"{package_name}".lower()))):
                shutil.rmtree(os.path.join(package_dir, f"{package_name}".lower()))
            
            json_file_path = os.path.join(os.path.expanduser("~/.modular"), 'environments.json') 
            with open(json_file_path, 'r') as f:
                environments = json.load(f)
                
            for env in environments:
                if env['name'] == active_env:
                    for i, pkg in enumerate(env['packages']):
                        if pkg['name'] == package_name:
                            del env['packages'][i]
                            break 
                
            with open(json_file_path, 'w') as f:
                json.dump(environments, f, indent=4)
                
            print(f"Package {package_name} removed successfully.")

        except FileNotFoundError as e:
            raise (f"Package {package_name} not found. {e}")
    
    def activate_env(self, env_name):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        if not os.path.exists(active_env_file_path):
            with open(active_env_file_path, 'w') as file:
                active = {"active_environment": "base"}
                json.dump(active, file)
                
        with open(active_env_file_path, 'r') as file:
            active_env = json.load(file)
        if active_env['active_environment'] == env_name:
            print(f"Environment '{env_name}' is already active.")
            return
        base_dir = os.path.expanduser("~/.modular/pkg/packages.modular.com_mojo/lib")
        env_dir = os.path.join(base_dir, env_name)
        cfg_file_path = os.path.expanduser("~/.modular/modular.cfg")
        if not os.path.exists(env_dir):
            print(f"Environment '{env_name}' does not exist.")
            return
        with open(cfg_file_path, 'r') as file:
            cfg_data = file.readlines()
        with open(cfg_file_path, 'w') as file:
            for line in cfg_data:
                if line.startswith("import_path"):
                    file.write(f"import_path = {env_dir}\n")
                else:
                    file.write(line)
                    
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'w') as file:
            json.dump({"active_environment": env_name}, file, indent=4)         
        print(f"Environment '{env_name}' activated. Use 'deactivate_env.py' to deactivate.")

    def deactivate_env(self):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'r') as file:
            temp = json.load(file)
        env_name = temp['active_environment']
        if env_name == "base":
            print("Cannot deactivate the base environment")
            return 
        base_dir = os.path.expanduser("~/.modular/pkg/packages.modular.com_mojo/lib")
        env_dir = os.path.join(base_dir, "base")
        cfg_file_path = os.path.expanduser("~/.modular/modular.cfg")
        if not os.path.exists(env_dir):
            print(f"Environment '{env_name}' does not exist.")
            return
        with open(cfg_file_path, 'r') as file:
            cfg_data = file.readlines()
            
        with open(cfg_file_path, 'w') as file:
            for line in cfg_data:
                if line.startswith("import_path"):
                    file.write(f"import_path = {env_dir}\n")
                else:
                    file.write(line)

        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'w') as file:
            json.dump({"active_environment": "base"}, file, indent=4) 
        print("Environment deactivated.")

    def current_env(self):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active.json')
        with open(active_env_file_path, 'r') as file:
            active_env = json.load(file)
        print(f"Current environment: {active_env['active_environment']}")

def main():
    parser = argparse.ArgumentParser(description="Package Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    parser_create = subparsers.add_parser('create', help='create environment')
    parser_create.add_argument("env_name", help="Name of the environment to create")

    parser_remove = subparsers.add_parser('remove', help='remove environment')
    parser_remove.add_argument("env_name", help="Name of the environment to remove")
    
    parser_activate = subparsers.add_parser('activate', help='activate environment')
    parser_activate.add_argument("env_name", help="Name of the environment to activate")

    parser_deactivate = subparsers.add_parser('deactivate', help='deactivate environment')
    
    parser_current = subparsers.add_parser('current', help='current environment')

    parser_install = subparsers.add_parser('install', help='install packages')
    parser_install.add_argument("package_name", help="Name of the package to install")
    parser_install.add_argument("--branch", action='store_true', help="Search for branches")

    parser_search = subparsers.add_parser('search', help='search package')
    parser_search.add_argument("package_name", help="Name of the package to search")

    parser_uninstall = subparsers.add_parser('uninstall', help='uninstall package')
    parser_uninstall.add_argument("package_name", help="Name of the package to uninstall")

    args = parser.parse_args()

    manager = PackageManager()

    if args.command == "create":
        manager.create(args.env_name)
    elif args.command == "uninstall":
        manager.uninstall(args.package_name)
    elif args.command == "install":
        manager.install_package(args.package_name, branch=args.branch)
    elif args.command == "activate":
        manager.activate_env(args.env_name)
    elif args.command == "deactivate":
        manager.deactivate_env()
    elif args.command == "current":
        manager.current_env()
    elif args.command == "search":
        manager.search_package(args.package_name)
    elif args.command == "remove":
        manager.remove(args.env_name)
    else:
        print("Invalid command specified. Use -h to see available commands.")

if __name__ == "__main__":
    main()
