import os
import requests
import shutil
import subprocess
import datetime
import json
import sys
import urllib.request
import re

class PackageManager:
    def __init__(self):
        self.home_dir = os.path.expanduser("~/.tenka")
    
    def search_package(self, package_name: str):
        url = f"https://api.github.com/search/repositories?q={package_name}+language:mojo"
        response = requests.get(url)
        if response.status_code == 200:
            search_results =  response.json()['items']
            print(f"Package {package_name} found successfully at {search_results[0]['html_url']}")
            return search_results
        else:
            raise Exception("Failed to search GitHub")
        
    def get_branches(self, repo_name: str):
        url = f"https://api.github.com/repos/{repo_name}/branches"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch branches")

    def download_package(self, repo_url, package_name, branch='main', env_name='base'):
        download_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            package_path = os.path.join(self.home_dir, f"envs/{env_name}/pkg/packages.modular.com_mojo/lib/mojo/{package_name}.zip")
            with open(package_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return package_path
        else:
            raise Exception("Failed to download package")

    def install_package(self, package_name, branch=False, active_env="base"):
        try:
            active_env = active_env
            if not active_env:
                raise ValueError("No active environment found")

            # Search for package
            search_results = self.search_package(package_name)
            if not search_results:
                print(f"No package found for {package_name}")
                return

            repo = search_results[0]
            repo_url = repo['html_url']
            repo_full_name = repo['full_name']
            
            # Get branches and select one
            branches = self.get_branches(repo_full_name)
            if branch is True and len(branches) > 1:
                branch = self._select_branch(branches)
            else:
                branch = 'main'
            
            # Download and unpack package
            package_path = self.download_package(repo_url, package_name, branch, active_env)
            env_package_path = os.path.join(self.home_dir, "envs", active_env, "pkg", "packages.modular.com_mojo", "lib", "mojo")
            shutil.unpack_archive(package_path, env_package_path)
            os.remove(package_path)
            package_directory = os.path.join(env_package_path, f"{package_name}-{branch}".lower())

            # Process package
            self._process_package(package_name, package_directory, env_package_path)

            # Update environments.json
            self._update_environments_json(active_env, package_name, branch)

            print(f"Package {package_name} installed successfully.")
                
        except Exception as e:
            print(f"Error installing package {package_name}: {str(e)}")

    def _select_branch(self, branches):
        print("Available branches:")
        for i, branch in enumerate(branches, 1):
            print(f"{i}. {branch['name']}")
        while True:
            choice = input("Choose a branch number (or press Enter for main): ")
            if choice == "":
                return 'main'
            try:
                branch_index = int(choice) - 1
                if 0 <= branch_index < len(branches):
                    return branches[branch_index]['name']
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _process_package(self, package_name, package_directory, env_package_path):
        try:
            os.chdir(package_directory)
            if os.path.exists(package_name + ".mojopkg"):
                mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                shutil.move(mojopkg_path, env_package_path)
            elif os.path.exists(package_name):
                subprocess.run(["mojo", "package", package_name], check=True, capture_output=True, text=True)
                mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                shutil.move(mojopkg_path, env_package_path)
            elif os.path.exists("src"):
                subprocess.run(["mojo", "package", "src", "-o", f"./{package_name}.mojopkg"], check=True, capture_output=True, text=True)
                mojopkg_path = os.path.join(package_directory, f"{package_name}.mojopkg")
                shutil.move(mojopkg_path, env_package_path)
            else:
                raise FileNotFoundError(f"No src or {package_name} found to package")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to package {package_name}: {e.stderr}")
        finally:
            shutil.rmtree(package_directory)

    def _update_environments_json(self, active_env, package_name, branch):
        json_file_path = os.path.join(os.path.expanduser("~/.tenka"), 'environments.json')
        package_info = {
            'name': package_name,
            'branch': branch,
            'install_date': datetime.datetime.now().date().isoformat()
        }
        
        try:
            with open(json_file_path, 'r+') as f:
                environments = json.load(f)
                if active_env not in environments:
                    environments[active_env] = {
                        'name': active_env,
                        'version': environments[active_env]['version'],
                        'description': environments[active_env]['description'],
                        'created': environments[active_env]['created'],
                        'packages': []
                    }
                environments[active_env]['packages'].append(package_info)
                f.seek(0)
                json.dump(environments, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            print(f"File {json_file_path} not found")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {json_file_path}")
        except KeyError as e:
            print(f"Key error when updating environments.json: {str(e)}")
        
    def uninstall(self, package_name, active_env="base"):
        if not active_env:
            raise ValueError("No active environment specified")

        env_package_path = os.path.join(self.home_dir, "envs", active_env, "pkg", "packages.modular.com_mojo", "lib", "mojo")
        package_path = os.path.join(env_package_path, f"{package_name}.mojopkg")

        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Package {package_name} not found in environment {active_env}")

        try:
            os.remove(package_path)
            print(f"Package {package_name} uninstalled successfully from {active_env} environment.")
        except OSError as e:
            raise OSError(f"Error removing package file: {str(e)}")

        json_file_path = os.path.join(os.path.expanduser("~/.tenka"), 'environments.json')
        
        try:
            with open(json_file_path, 'r+') as f:
                environments = json.load(f)
                if active_env not in environments:
                    raise KeyError(f"Active environment {active_env} not found in {json_file_path}")
                
                packages = environments[active_env].get('packages', [])
                packages = [pkg for pkg in packages if pkg['name'] != package_name]
                environments[active_env]['packages'] = packages
                
                f.seek(0)
                json.dump(environments, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            raise FileNotFoundError(f"Environments file not found: {json_file_path}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Error decoding JSON from {json_file_path}")
        except IOError as e:
            raise IOError(f"Error updating environments file: {str(e)}")
            
    def list_all_packages(self, active_env="base"):
        active_env = active_env

        json_file_path = os.path.join(os.path.expanduser("~/.tenka"), 'environments.json')
        with open(json_file_path, 'r') as f:
            environments = json.load(f)
            print(f"\n--- Packages installed in {active_env} ---\n")
            if environments[active_env]['packages']:
                print(f"{'Package Name':<20} {'Branch':<15}")
                print("-" * 50)
                for package in environments[active_env]['packages']:
                    print(f"{package['name']:<20} {package['branch']:<15}")
            else:
                print("No external packages installed")

    # TODO: list all dates of release too
    def list_mojo(self):
        url = "https://docs.modular.com/mojo/changelog"
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
            
            version_pattern = r'<a class="table-of-contents__link toc-highlight" href="/mojo/changelog#(v[\d.]+)-.*?">(v[\d.]+)\s*\(.*?\)</a>'
            versions = re.findall(version_pattern, html)
            
            if not versions:
                raise ValueError("No versions found in the changelog")
            
            print("\n--- Available Mojo Versions ---")
            for i, version in enumerate(versions, start=1):
                version = f"{version[1][1:]}.0" if len(version[1][1:]) == 4 else version[1][1:]
                print(f"{i}. {version}")
            
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to fetch the changelog: {e}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while getting the version map: {e}")
    
    def list_all_environments(self):
        json_file_path = os.path.join(os.path.expanduser("~/.tenka"), 'environments.json')
        with open(json_file_path, 'r') as f:
            environments = json.load(f)
            print("\n--- Tenka Environments ---\n")
            print(f"{'Environment':<15} {'Version':<10} {'Description':<40}")
            print("-" * 65)
            for env_name, env_data in environments.items():
                print(f"{env_name:<15} {env_data['version']:<10} {env_data['description']:<40}")

if __name__ == "__main__":
    manager = PackageManager()
    if len(sys.argv) < 2:
        print("Usage: python environments.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "install" and len(sys.argv) == 5:
        manager.install_package(sys.argv[2], branch=sys.argv[3], active_env=sys.argv[4])
    elif command == "uninstall" and len(sys.argv) == 4:
        manager.uninstall(sys.argv[2], active_env=sys.argv[3])
    elif command == "search" and len(sys.argv) == 3:
        manager.search_package(sys.argv[2])
    elif command == "list-pkgs" and len(sys.argv) == 3:
        manager.list_all_packages(active_env=sys.argv[2])
    elif command == "list-envs" and len(sys.argv) == 2:
        manager.list_all_environments()
    elif command == "list-mojo" and len(sys.argv) == 2:
        manager.list_mojo()
    else:
        print("Usage: python environments.py <command> [<args>]")
        sys.exit(1)
