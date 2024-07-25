<a name="readme-top"></a>

<div align="center">
  <a href="">
    <img src="./assets/tenka_logo.png" alt="Logo" width="350" height="350">
  </a>

  <h1 align="center" style="font-size: 3em; color: white; font-family: 'Avenir'; text-shadow: 1px 1px red;">Tenka 点火</h1>

  <p align="center">
    A powerful package manager for the Mojo 🔥 programming language
  </p>
</div>

<p align="center">
    <hr style="border-top: 1px solid white; width: 100%; margin: 20px 0;">
</p>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#features">Features & Usage</a>
      <ul>
        <li><a href="#environment-management">Environment management </a></li>
        <li><a href="#package-management">Package management</a></li>
        <li><a href="#module-packaging">Module packaging</a></li>
      </ul>
    </li>
    <li>
      <a href="#get-started">Get started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#uninstallation">Uninstallation</a></li>
      </ul>
    </li>
    <li><a href="#limitations">Limitations</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

# Tenka 🔥: Ignite Your Mojo Development

Tenka (点火, "ignition" in Japanese) is a robust package manager designed specifically for the Mojo programming language. It aims to streamline your development process by providing an intuitive way to manage Mojo environments and packages.

## Features & Usage

### Environment Management

Tenka provides powerful tools for managing your Mojo environments:

- **Create Environments**: Set up isolated Mojo environments with ease.
  ```
  tenka create <env_name> [<version>]
  ```
  This command creates a new environment with an optional Mojo version (defaults to the latest). Mojo versions follow the convention found in the [Mojo changelog](https://docs.modular.com/mojo/changelog).

- **Activate Environments**: Seamlessly switch between different Mojo setups.
  ```
  tenka activate <env_name>
  ```
  Activate a specific environment for your current session.

- **Deactivate Environments**: Step out of the current environment when needed.
  ```
  tenka deactivate
  ```
  This command deactivates the currently active environment. If base environment is deactivated, it returns to the default mojo installation in the system at `~/.modular`.

- **Delete Environments**: Easily remove unused environments to free up space.
  ```
  tenka delete <env_name>
  ```
  Permanently delete a specified environment.

- **List Environments**: View all available environments.
  ```
  tenka list-envs
  ```

- **List Mojo**: View all available official Mojo release versions.
  ```
  tenka list-mojo
  ```

### Package Management

Tenka simplifies the process of managing Mojo packages:

- **Install Packages**: Add new packages to your environment effortlessly.
  ```
  tenka install <package_name> [<branch_name>]
  ```
  Install a package, with an optional ability to specify a branch of the GitHub repository.

- **Search Packages**: Quickly find Mojo packages on GitHub.
  ```
  tenka search <package_name>
  ```
  Search for available packages matching your query.

- **Uninstall Packages**: Remove unwanted packages from your active environment.
  ```
  tenka uninstall <package_name>
  ```
  Uninstall a specified package from the current environment.

- **List Packages**: View all installed external packages in the current active environment.
  ```
  tenka list-pkgs
  ```

### Module Packaging

Tenka allows you to create and manage your own Mojo packages:

- **Package Local Modules**: Convert your Mojo modules into packages.
  ```
  tenka package <source_name> <package_name> [<source_path>]
  ```
  This command packages a local Mojo module and adds it to the current environment. 
  - `<source_name>`: The name of the folder containing the .mojo files
  - `<package_name>`: The name of the package when imported in Mojo
  - `<source_path>`: (Optional) The path to the source folder. If not provided, Tenka will look in the current directory.
Example: 
  ```
  tenka package src xyz
  ```
  This example searches the current directory and packages the `src` module so that it can be imported as `xyz` inside Mojo.

## Get Started

### Installation
1. Clone the Tenka repository:
   ```
   git clone https://github.com/shivasankarka/Tenka.git
   ```
2. Navigate to the Tenka directory:
   ```
   cd tenka
   ```
3. Run the setup file:
   ```
   python setup_tenka.py
   ```

### Uninstallation

To remove Tenka from your system, follow these steps:

1. Delete the Tenka directories:
   ```
   rm -rf ~/.tenka
   ```

2. Open your `.zshrc` file using your preferred text editor:
   ```
   nano ~/.zshrc
   ```

3. Find and remove the following lines:
   ```
   # Tenka Package Manager
   tenka () {
       source $HOME/.tenka/bin/tenka.sh
       tenka_cli "$@"
   }
   export MODULAR_HOME="..."
   export PATH="..."
   export TENKA_ACTIVE_ENV="base"
   export TENKA_ACTIVE_VERSION="..."
   ```
4. Insert the following lines:
    ```
    MOJO_PATH = "'$HOME'/.modular/pkg/packages.modular.com_mojo" 
    export MODULAR_HOME="'$HOME'/.modular"
    export PATH="'$MOJO_PATH'/bin:$PATH"
    ```
5. Save your changes and exit the editor.

6. Refresh your shell configuration:
   ```
   source ~/.zshrc
   ```

After completing these steps, Tenka will be completely removed from your system and you can use the default mojo version installed through modular.

## Limitations

Tenka is a powerful package manager, but it does have some limitations to be aware of:

1. GitHub Project Installation:
   - Tenka requires GitHub projects to have a main package directory with the same name as the repository.
   - For example, a repository named "xyz" should have a source directory named "xyz" or "src".
   - Projects with differently named source directories (e.g., "xyzud") cannot be installed or packaged by Tenka.

2. Shell Compatibility:
   - Currently, Tenka is only compatible with zsh on macOS.
   - It relies on zsh scripts for handling operations.
   - If you're interested in contributing to bash support, please open a pull request or issue on our GitHub repository.

3. Package Dependencies:
   - Due to the lack of a standard Mojo package versioning system, Tenka cannot verify if a package will function correctly within a specific Mojo environment.
   - This limitation may affect the reliability of package installations in certain scenarios.

Active work is being done to address these limitations. If you have any suggestions or would like to contribute, please feel free to reach out or submit a pull request or issue. 

## Contributing

Any contributions to Tenka are welcome! If you have ideas, suggestions, or bug reports, please don't hesitate to open an issue or submit a pull request on the GitHub repository.

## License
Distributed under the Apache 2.0 License with LLVM Exceptions. See [LICENSE](https://github.com/Mojo-Numerics-and-Algorithms-group/NuMojo/blob/main/LICENSE) and the LLVM [License](https://llvm.org/LICENSE.txt) for more information.

I hope it makes your Mojo package management a breeze.
