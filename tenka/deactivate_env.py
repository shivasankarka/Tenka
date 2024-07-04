import os

def deactivate_env():
    if "MOJO_ENV" in os.environ:
        del os.environ["MOJO_ENV"]
        print("Environment deactivated.")
    else:
        print("No environment is currently activated.")

if __name__ == "__main__":
    deactivate_env()