import requests
import os
import zstandard
import tarfile
import io
import sys
from packages import get_latest_version_map, get_latest_version

def download_package(version, env_name="base"):
    version_map = get_latest_version_map()
    # version_map = {
    # "24.4.0": 14,
    # "24.3.0": 13,
    # "24.2.1": 12,
    # "24.2.0": 11,
    # "24.1.1": 10,
    # "24.1.0": 9,
    # "0.7.0": 8,
    # "0.6.1": 7,
    # "0.6.0": 6,
    # "0.5.0": 5,
    # "0.4.0": 4,
    # "0.3.1": 3,
    # "0.3.0": 2,
    # "0.2.1": 1
    # }
    number = version_map.get(version, 0) 
    base_url = "https://packages.modular.com/mojo"
    file_name = f"mojo-arm64-apple-darwin22.6.0-{version}-{number}-0.tar.zst"
    url = f"{base_url}/packages/{version}/{file_name}"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        package_path = os.path.expanduser(f"~/.tenka/envs/{env_name}/pkg/packages.modular.com_mojo/{file_name}")
        with open(package_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        extract_package(package_path)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def extract_package(file_path: str):
    try:
        with open(file_path, 'rb') as compressed_file:
            dctx = zstandard.ZstdDecompressor()
            with dctx.stream_reader(compressed_file) as reader:
                with tarfile.open(fileobj=io.BytesIO(reader.read())) as tar:
                    tar.extractall(path=os.path.dirname(file_path))
        os.remove(file_path)  
    except Exception as e:
        print(f"An error occurred during extraction: {e}")

def main(version, env_name="base"):
    latest_version = get_latest_version()
    download_package(version=latest_version, env_name=env_name)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(version=sys.argv[1], env_name=sys.argv[2])
    else:
        print("Usage: python download.py <version> <env_name>")