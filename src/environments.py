import os 
import json
import sys
import datetime

def get_all_envs():
    try:
        with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
            envs = json.load(f)
            for env in envs:
                print(f"{env}- Mojo@{envs[env]['version']}")
    except FileNotFoundError:
        print("Error: Environments file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in environments file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def create_environment(env_name: str, version: str = "24.4.0"):
    try:
        environments_file = os.path.expanduser('~/.tenka/environments.json')
        with open(environments_file, 'r+') as f:
            envs = json.load(f)
            if env_name in envs:
                print(f"Environment '{env_name}' already exists.")
                sys.exit(0)

            new_env = {
                env_name: {
                    'name': env_name, 
                    'version': version,
                    'description': f"Environment {env_name} with Mojo {version}",
                    'created': datetime.datetime.now().isoformat(),
                    'packages': []
                }
            }
            envs.update(new_env)
            f.seek(0)
            json.dump(envs, f, indent=4)
            f.truncate()

        modular_cfg_path = os.path.expanduser(f'~/.tenka/envs/{env_name}/modular.cfg')
        with open(modular_cfg_path, 'r+') as cfg:
            content = cfg.read()
            content = content.replace(os.path.expanduser('~/.tenka/envs/base'), os.path.expanduser(f'~/.tenka/envs/{env_name}'))
            cfg.seek(0)
            cfg.write(content)
            cfg.truncate()
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Required file not found. Please check if '{environments_file}' and '{modular_cfg_path}' exist.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in environments file.")
    except PermissionError:
        print("Error: Permission denied. Unable to write to the required files.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def delete_environment(env_name: str):
    with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
        envs = json.load(f)
        if env_name in envs:
            envs.pop(env_name)
            with open(os.path.expanduser('~/.tenka/environments.json'), 'w+') as f:
                json.dump(envs, f, indent=4)
            sys.exit(1)
        else:
            sys.exit(0)
   
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python environments.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create_environment" and len(sys.argv) == 4:
        create_environment(sys.argv[2], sys.argv[3])
    elif command == "delete_environment" and len(sys.argv) == 3:
        delete_environment(sys.argv[2])
    elif command == "get_all_envs" and len(sys.argv) == 2:
        get_all_envs()
    else:
        print("Invalid command or arguments")
        print("Available commands:")
        print("  create_environment <env_name>")
        print("  delete_environment <env_name>")
        print("  get_all_envs")
        sys.exit(1)
