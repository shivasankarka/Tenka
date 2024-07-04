import os
import sys

def activate_env(env_name):
    base_dir = os.path.expanduser("~/.modular_envs")
    env_dir = os.path.join(base_dir, env_name)
    
    if not os.path.exists(env_dir):
        print(f"Environment '{env_name}' does not exist.")
        return
    
    os.environ["MOJO_ENV"] = env_dir
    print(f"Environment '{env_name}' activated. Use 'deactivate_env.py' to deactivate.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: activate_env.py <env_name>")
    else:
        activate_env(sys.argv[1])