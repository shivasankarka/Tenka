import datetime
import os
import json
import sys
import urllib.request
import re

def update_package_metadata(active_env: str, package_name: str, branch: None):
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
                    'version': '',
                    'description': '',
                    'created': datetime.datetime.now().isoformat(),
                    'packages': []
                }
            environments[active_env]['packages'].append(package_info)
            f.seek(0)
            json.dump(environments, f, indent=4)
            f.truncate()
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}. Please check the file contents.")
    except IOError as e:
        print(f"Error: An I/O error occurred while accessing {json_file_path}: {str(e)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

def get_latest_version():
    url = "https://docs.modular.com/mojo/changelog"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        
        version_pattern = r'<a class="table-of-contents__link toc-highlight" href="/mojo/changelog#(v[\d.]+)-.*?">(v[\d.]+)\s*\(.*?\)</a>'
        versions = re.findall(version_pattern, html)

        if versions:
            version = versions[0][1][1:]
            if len(version) == 4:
                return version + ".0"
            else:
                return version
        else:
            print("Error: No versions found in the changelog.")
            return None
    except urllib.error.URLError as e:
        print(f"Error: Failed to fetch the changelog: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while fetching the latest version: {e}")
    return None

if __name__ == "__main__":
    if sys.argv[1] == "update_package_metadata":
        update_package_metadata(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "get_latest_version":
        get_latest_version()
    else:
        print("Invalid command")
        sys.exit(1)