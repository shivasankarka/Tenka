import os
import shutil
import sys

def create_env(env_name):
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