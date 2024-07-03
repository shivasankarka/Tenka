# Tenka

Tenka is a powerful and user-friendly Python package manager tailored for the Mojo programming language. The name `Tenka` is derived from the Japanese word `点火`, meaning "ignition," symbolizing my mission to fuel your Mojo's 🔥 capabilities and your development journey with ease and efficiency.

With Tenka, you can effortlessly search and install from github, and remove Mojo packages in your projects, making your development process smoother and more efficient. 

## Features

- **Search Packages**: Quickly find the Mojo packages you need.
- **Install Packages**: Easily install Mojo packages from GitHub repositories.
- **Remove Packages**: Cleanly remove unwanted Mojo packages from your projects.

## Long terms goals
- Ability to create and deactivate virtual environments
- Ability to install packages to specific environments
- Better control over package installation from GitHub
- Improved dependency management
- Support for package versioning

## Installation

To get started with Tenka, you can install it using pip. Follow these simple steps:

1. Navigate to the `tenka` directory:
    ```
    cd tenka
    ```
2. Install Tenka in editable mode:
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

## Contributing

Any contributions to tenka are welcome! If you have any ideas, suggestions, or bug reports, please feel free to open an issue or submit a pull request on our GitHub repository.

## License

Tenka is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

I hope it makes your Mojo package management a breeze.
