import requests
import os
import zstandard
import tarfile
import io
import sys
import urllib.request
import re

def get_latest_version():
    url = "https://docs.modular.com/mojo/changelog"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        
        version_pattern = r'<a class="table-of-contents__link toc-highlight" href="/mojo/changelog#(v[\d.]+)-.*?">(v[\d.]+)\s*\(.*?\)</a>'
        versions = re.findall(version_pattern, html)

        if versions:
            version = versions[0][1][1:]
            return f"{version}.0" if len(version) == 4 else version
        else:
            raise ValueError("No versions found in the changelog")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch the changelog: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while getting the latest version: {e}")

def get_latest_version_map():
    url = "https://docs.modular.com/mojo/changelog"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        
        version_pattern = r'<a class="table-of-contents__link toc-highlight" href="/mojo/changelog#(v[\d.]+)-.*?">(v[\d.]+)\s*\(.*?\)</a>'
        versions = re.findall(version_pattern, html)
        
        if not versions:
            raise ValueError("No versions found in the changelog")
        
        version_map = {}
        versions = [v[1][1:] for v in versions]  # Extract version numbers
        versions.sort(key=lambda v: [int(n) for n in v.split('.')])  # Sort versions
        for i, version in enumerate(versions, start=1):
            version = f"{version}.0" if len(version) == 4 else version
            version_map[version] = i
        
        return version_map
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch the changelog: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while getting the version map: {e}")

def download_package(version, env_name="base"):
    try:
        version_map = get_latest_version_map()
        number = version_map.get(version)
        if number is None:
            raise ValueError(f"Version {version} not found in the version map")
        
        base_url = "https://packages.modular.com/mojo"
        file_name = f"mojo-arm64-apple-darwin22.6.0-{version}-{number}-0.tar.zst"
        url = f"{base_url}/packages/{version}/{file_name}"
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        package_path = os.path.expanduser(f"~/.tenka/envs/{env_name}/pkg/packages.modular.com_mojo/{file_name}")
        os.makedirs(os.path.dirname(package_path), exist_ok=True)
        
        with open(package_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        extract_package(package_path)
        print(f"Successfully downloaded and extracted Mojo version {version}")
    except ValueError as e:
        print(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading package: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def extract_package(file_path: str):
    try:
        with open(file_path, 'rb') as compressed_file:
            dctx = zstandard.ZstdDecompressor()
            with dctx.stream_reader(compressed_file) as reader:
                with tarfile.open(fileobj=io.BytesIO(reader.read())) as tar:
                    tar.extractall(path=os.path.dirname(file_path))
        os.remove(file_path)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found")
    except tarfile.TarError as e:
        print(f"Error extracting tar file: {e}")
    except zstandard.ZstdError as e:
        print(f"Error decompressing zstandard file: {e}")
    except PermissionError:
        print(f"Error: Permission denied when trying to remove {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")

def main(version=None, env_name="base"):
    try:
        if version is None:
            version = get_latest_version()
            print(f"Using latest version: {version}")
        download_package(version=version, env_name=env_name)
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(version=sys.argv[1], env_name=sys.argv[2])
    elif len(sys.argv) == 2:
        main(version=sys.argv[1])
    else:
        print("Usage: python download.py [<version>] [<env_name>]")
        # print("If version is not provided, the latest version will be used.")
        # print("If env_name is not provided, 'base' will be used.")