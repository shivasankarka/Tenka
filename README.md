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

With Tenka, you can effortlessly search and install from github, and remove Mojo packages in your projects, making your development process smoother and more efficient. 

## Features

- **Create & Remove environments**: Easily create virtual environments to isolate your projects and manage their dependencies and remove them easily. 
- **Activate and deactivate environments**: Switch between different environments to work on different projects without conflicts.
- **Install packages**: Install packages directly into a specific environment, ensuring that your project has the necessary dependencies.
- **Search Packages**: Quickly find the Mojo packages you need from Github.
- **Uninstall Packages**: Cleanly remove unwanted Mojo packages from your projects.

## Long terms goals
- Ability to create and deactivate mojo environments with different mojo versions.
- Better control over package installation from GitHub
- Improved dependency management
- Support for package versioning

## Installation

To get started with Tenka, you can install it using pip. Follow these simple steps:

1. Clone the Tenka repository:
    ```
    git clone https://github.com/your-username/tenka.git
    ```
2. Navigate to the `tenka` directory:
    ```
    cd tenka
    ```
3. Install Tenka in editable mode:
    ```
    pip install -e .
    ```

## Usage

Once installed, you can use Tenka through the command line interface (CLI). Here are some basic commands:

- **Install a package**:
    ```
    tenka install <package_name> [--branch]
    ```
    Use the `--branch` option to specify a branch if needed.

- **Search for a package**:
    ```
    tenka search <package_name>
    ```

- **Remove a package**:
    ```
    tenka remove <package_name>
    ```

- **Create an environment**:
    ```
    tenka create <env_name>
    ```
    Specify the name of the environment to create.

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

## Current Limitations:
- **Mojo Version Management**: Tenka is currently working on supporting the management of different Mojo versions.
- **GitHub Project Installation Limitation**: Tenka cannot install and package GitHub projects that do not adhere to the standard naming convention for their directories. For example, a repository named "xyz" should have a source directory named "xyz", not "xyzu".

## Contributing

Any contributions to tenka are welcome! If you have any ideas, suggestions, or bug reports, please feel free to open an issue or submit a pull request on our GitHub repository.

## License

Tenka is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

I hope it makes your Mojo package management a breeze.
