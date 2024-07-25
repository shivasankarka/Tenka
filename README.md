<a name="readme-top"></a>

<div align="center">
  <a href="">
    <img src="./assets/tenka_logo.png" alt="Logo" width="350" height="350">
  </a>


  <h1 align="center" style="font-size: 3em; color: white; font-family: 'Avenir'; text-shadow: 1px 1px red;">Tenka 点火</h1>

  <p align="center">
    Tenka is a package manager for Mojo 🔥 programming language written in python in the likes of conda. 
  </p>
</div>
<p align="center">
    <hr style="border-top: 1px solid white; width: 100%; margin: 20px 0;">
</p>

Tenka is a powerful and user-friendly package manager tailored for the Mojo programming language. The name `Tenka` is derived from the Japanese word `点火`, meaning "ignition," symbolizing my mission to fuel Mojo's 🔥 capabilities and your development journey with ease and efficiency.

With Tenka, you can effortlessly create, delete environments with different Mojo versions. You can search and install packges from github, and remove Mojo packages from environments, making your development process smoother and more efficient. 

## Features

- **Create & Remove Environments**: Easily create virtual environments to isolate your projects, manage their dependencies, and remove them effortlessly.
- **Activate and Deactivate Environments**: Seamlessly switch between different environments to work on various projects without conflicts.
- **Install Packages**: Directly install packages into a specific environment to ensure your project has all necessary dependencies.
- **Search Packages**: Quickly find the Mojo packages you need from GitHub.
- **Uninstall Packages**: Safely remove unwanted Mojo packages from your projects.
- **Package Modules**: Package local Mojo modules directly and add them to the currently active environment.

## Long terms goals
- Better control over package installation from GitHub
- Improved dependency management
- Support for package versioning

## Setting upx

### Installation
To get started with Tenka, you can install it using pip. Follow these simple steps:

1. Clone the Tenka repository:
    ```
    git clone https://github.com/shivasankarka/Tenka.git
    ```
2. Navigate to the `tenka` directory:
    ```
    cd tenka
    ```
3. Install Tenka in editable mode:
    ```
    python setup_tenka.py
    ```
This will install `Tenka` to the `$HOME` path. You can remove the downloaded files after installation.  

### Uninstall
To uninstall Tenka, Follow these steps,

1. Uninstall it using the following command
    ```
    rm -rf ~/.tenka 
    ```

## Usage
Once installed, you can use Tenka through the command line interface (CLI). Here are some basic commands:

- **Create an environment**:
    To create a new environment, use the following command:
    ```
    tenka create <env_name> [<version>]
    ```
    You can specify the name of the environment to create. The `<version>` parameter is optional, and if not provided, Tenka will install the latest Mojo version by default (Currently 24.4.0).

- **Activate an environment**:
    ```
    tenka activate <env_name>
    ```
    Specify the name of the environment to activate.

- **Deactivate the current environment**:
    ```
    tenka deactivate
    ```
    No arguments needed.

- **Remove an environment**:
    ```
    tenka remove <env_name>
    ```
    Specify the name of the environment to remove.

- **Package a Mojo modular**:
    ```
    tenka package <source_name> <package_name> [<source_path>]
    ```
    Specify the name of the source module and the package name to be used when importing the package. `<source_path>` is optional; if nott provided, Tenka will search it in current path automatically package and add it to the active environment. 

- **Install a package**:
    ```
    tenka install <package_name> [--branch]
    ```
    Use the `--branch` option to specify a branch if needed. Tenka will install the package to the current active environment.

- **Search for a package**:
    ```
    tenka search <package_name>
    ```
    This command searches for a package named `<package_name>` on GitHub.

- **Remove a package**:
    ```
    tenka remove <package_name>
    ```
    This command removes the package named `<package_name>`.
    

- **GitHub Project Installation Limitation**: Tenka is unable to install and package GitHub projects that do not have a main package directory with the same name as the repository. For instance, a repository named "xyz" should have a source directory named "xyz" or "src", not "xyzud".
- **Bash Support**: Tenka currently relies on zsh scripts for handling operations and therefore is only compatible with zsh on macOS. If you are interested in contributing to bash development, please open a pull request or issue and get in touch with me.
- **Package dependencies**: Currently, As there are no standard Mojo package versioning system, Tenka lacks the capability to verify if a package will function correctly within a specific Mojo environment.

## Contributing

Any contributions to Tenka are welcome! If you have ideas, suggestions, or bug reports, please don't hesitate to open an issue or submit a pull request on the GitHub repository.

## License
Tenka is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

I hope it makes your Mojo package management a breeze.
