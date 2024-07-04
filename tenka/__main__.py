import os
import requests
import shutil
import subprocess
import argparse
import datetime
import json

class PackageManager:
    def __init__(self, env_name="base"):
        self.env = env_name
        self.home_directory = os.path.expanduser("~/.modular/pkg/packages.modular.com_mojo/lib")
        if not os.path.exists(os.path.join(self.home_directory, "base")):
            try:
                shutil.copytree(self.home_directory+"/mojo/", self.home_directory+"/base/")
            except shutil.Error as e:
                print(f"Error copying files: {e}")
                shutil.rmtree(self.home_directory+"/base")
                return

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
        
    def remove_package(self, env_name):
        shutil.rmtree(os.path.join(self.home_directory, env_name))
        json_file_path = os.path.join(self.home_directory, 'environments.json')
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
        json_file_path = os.path.join(self.home_directory, 'environments.json')
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
                    # Overwrite existing environment info
                    environments[i] = environment_info
                    break
                else:
                    environments.append(environment_info)
        else:
            environments = [environment_info]
        
        with open(json_file_path, 'w') as f:
            json.dump(environments, f, indent=4)
        
        print(f"Environment information saved to {json_file_path}")

    def uninstall(self, package_name):
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
    
    def activate_env(self, env_name):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active_environment.json')
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
                    
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active_environment.json')
        with open(active_env_file_path, 'w') as file:
            json.dump({"active_environment": env_name}, file, indent=4)
        # zshrc_path = os.path.expanduser("~/.zshrc")
        # with open(zshrc_path, "a") as zshrc_file:
        #     zshrc_file.write(f'export PS1="({env_name}) $PS1"\n')
        # os.system(f'source {zshrc_path}')
        # os.system('source ~/.zshrc')
         
        print(f"Environment '{env_name}' activated. Use 'deactivate_env.py' to deactivate.")

    def deactivate_env(self, env_name):
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

        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active_environment.json')
        with open(active_env_file_path, 'w') as file:
            json.dump({"active_environment": "base"}, file, indent=4) 
        # os.system('source ~/.zshrc')
        # zshrc_path = os.path.expanduser("~/.zshrc")        
        # with open(zshrc_path, "r") as zshrc_file:
        #     lines = zshrc_file.readlines()
        
        # with open(zshrc_path, "w") as zshrc_file:
        #     for line in lines:
        #         if "PS1" not in line:
        #             zshrc_file.write(line)
        # os.system(f'source {zshrc_path}')
        print("Environment deactivated.")

    def current_env(self):
        active_env_file_path = os.path.join(os.path.expanduser("~/.modular"), 'active_environment.json')
        with open(active_env_file_path, 'r') as file:
            active_env = json.load(file)
        print(f"Current environment: {active_env['active_environment']}")

def main():
    parser = argparse.ArgumentParser(description="Package Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    parser_create = subparsers.add_parser('create', help='create help')
    parser_create.add_argument("env_name", help="Name of the environment to create")

    parser_remove = subparsers.add_parser('remove', help='remove help')
    parser_remove.add_argument("env_name", help="Name of the environment to remove")
    
    parser_activate = subparsers.add_parser('activate', help='activate help')
    parser_activate.add_argument("env_name", help="Name of the environment to activate")

    parser_deactivate = subparsers.add_parser('deactivate', help='deactivate help')
    parser_deactivate.add_argument("env_name", help="Name of the environment to deactivate")

    parser_current = subparsers.add_parser('current', help='current help')

    parser_install = subparsers.add_parser('install', help='install help')
    parser_install.add_argument("package_name", help="Name of the package to install")
    parser_install.add_argument("--branch", action='store_true', help="Search for branches")

    parser_search = subparsers.add_parser('search', help='search help')
    parser_search.add_argument("package_name", help="Name of the package to search")

    parser_uninstall = subparsers.add_parser('uninstall', help='uninstall help')
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
        manager.deactivate_env(args.env_name)
    elif args.command == "current":
        manager.current_env()
    elif args.command == "search":
        manager.search_package(args.package_name)
    elif args.command == "remove":
        manager.remove_package(args.env_name)
    else:
        print("Invalid command specified. Use -h to see available commands.")

if __name__ == "__main__":
    main()
    # manager = PackageManager("base")
    # manager.create("conda")
    # manager.install_package("numojo")
    # manager.remove_package("numojo")