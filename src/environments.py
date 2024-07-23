import os 
import json
import sys
import datetime
import shutil

def get_all_envs():
    with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
        envs = json.load(f)
        for env in envs:
            print(f"{env}- Mojo@{envs[env]['version']}")

def create_environment(env_name: str, version: str = "24.4.0"):
    with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
        envs = json.load(f)
        if env_name in envs:
            sys.exit(0)
        else:
            new_env = {
                env_name: 
                    {'name': env_name, 
                     'version': version,
                     'description': f"Environment {env_name} with Mojo {version}",
                     'created': datetime.datetime.now().isoformat()
                     }
            }
            envs.update(new_env)
            with open(os.path.expanduser('~/.tenka/environments.json'), 'w+') as f:
                json.dump(envs, f, indent=4)  
            sys.exit(1)

def delete_environment(env_name: str):
    with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
        envs = json.load(f)
        if env_name in envs:
            envs.pop(env_name)
            with open(os.path.expanduser('~/.tenka/environments.json'), 'w+') as f:
                json.dump(envs, f, indent=4)
            shutil.rmtree(os.path.expanduser(f'~/.tenka/envs/{env_name}'))
            sys.exit(1)
        else:
            sys.exit(0)

def edit_cfg(env_name_init: str, env_name_final: str):
    home_dir = os.path.expanduser("~/.tenka")
    with open(os.path.join(home_dir, "modular.cfg"), "r+") as file:
        content = file.read()
        if env_name_init == "mojo":
            content = content.replace(os.path.join(os.path.expanduser("~"), ".modular/pkg/packages.modular.com_mojo"), f"{home_dir}/envs/{env_name_final}")
        if env_name_final == "mojo":
            content = content.replace(f"{home_dir}/envs/{env_name_init}", os.path.join(os.path.expanduser("~"), ".modular/pkg/packages.modular.com_mojo"))
        else:
            content = content.replace(f"{home_dir}/envs/{env_name_init}", os.path.join(home_dir, "envs", env_name_new))
        file.seek(0)
        file.write(content)
        file.truncate()
   
def change_active_env(env_name_new: str, version: str):
    with open(os.path.expanduser('~/.tenka/active.json'), 'w+') as f:
        json.dump({'active': env_name_new, 'version': version}, f)
    
def get_active_environment():
    with open(os.path.expanduser('~/.tenka/active.json'), 'r') as f:
        envs = json.load(f)
    print(envs['active'])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python environments.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create_environment" and len(sys.argv) == 3:
        create_environment(sys.argv[2])
    elif command == "delete_environment" and len(sys.argv) == 3:
        delete_environment(sys.argv[2])
    elif command == "edit_cfg" and len(sys.argv) == 4:
        edit_cfg(sys.argv[2], sys.argv[3])
    elif command == "change_active_env" and len(sys.argv) == 4:
        change_active_env(sys.argv[2], sys.argv[3])
    elif command == "get_active_environment" and len(sys.argv) == 2:
        get_active_environment()
    elif command == "get_all_envs" and len(sys.argv) == 2:
        get_all_envs()
    else:
        print("Invalid command or arguments")
        print("Available commands:")
        print("  create_environment <env_name>")
        print("  delete_environment <env_name>")
        print("  edit_cfg <env_name_init> <env_name_final>")
        print("  change_active_env <env_name> <version>")
        print("  get_active_environment")
        sys.exit(1)
