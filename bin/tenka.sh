
activate() {
    local new_env_name="$1"
    if [ -z "$new_env_name" ]; then
        echo "Error: Environment name not provided"
        return 1
    fi
    
    python -c "
import os 
import json
import sys

def check_env(env_name):
    env_json = os.path.expanduser('~/.tenka/environments.json')
    with open(env_json, 'r') as f:
        env = json.load(f)
        if env_name in env:
            sys.exit(1)  # success
        else:
            sys.exit(0)  # failure

check_env('$new_env_name')
"

    if [ $? -eq 0 ]; then
        echo "Error: Environment '$new_env_name' does not exist"
        return 1
    fi

    local current_env_path
    local current_env_name
    if echo "$PATH" | grep -q "${HOME}/.modular/pkg/packages.modular.com_mojo/bin"; then
        current_env_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        current_env_name="mojo"
    else
        current_env_path=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/pkg/packages.modular.com_mojo/bin" | head -n 1)
        current_env_name=$(echo "$current_env_path" | sed -n 's|.*/envs/\([^/]*\)/pkg/packages.modular.com_mojo/bin|\1|p')
    fi

    local new_path="${HOME}/.tenka/envs/${new_env_name}/pkg/packages.modular.com_mojo/bin"
    if [ ! -d "$new_path" ]; then
        echo "Error: Environment '$new_env_name' does not exist"
        return 1
    fi

    local new_env_version=$(python -c "
import os 
import json
with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
    envs = json.load(f)
    if '$new_env_name' in envs:
        print(envs['$new_env_name']['version'], end='')
    else:
        print('', end='')
")
    if [ -z "$new_env_version" ]; then
        echo "Error: Environment '$new_env_name' does not exist"
        return 1
    fi

    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$current_env_path$|$new_path|" | paste -sd: -)
    export MODULAR_HOME="$HOME/.tenka/envs/$new_env_name"

    export TENKA_ACTIVE_ENV="$new_env_name"
    export TENKA_ACTIVE_VERSION="$new_env_version"
    echo "Environment '$new_env_name' activated"
}

deactivate() {
    local active_env=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/pkg/packages.modular.com_mojo/bin" | head -n 1)
    if [ -z "$active_env" ]; then
        echo "No active Tenka environment found"
        return 1
    fi

    local current_env_name=$(echo "$active_env" | sed -n 's|.*/envs/\([^/]*\)/pkg/packages.modular.com_mojo/bin|\1|p')
    local new_path
    local new_env_version
    if [ "$current_env_name" = "base" ]; then
        new_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        new_env_version=$(python -c "
import os 
import json
with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
    envs = json.load(f)
    if 'base' in envs:
        print(envs['base']['version'], end='')
    else:
        print('', end='')
")
        export TENKA_ACTIVE_ENV="mojo"
        export TENKA_ACTIVE_VERSION="$new_env_version"
        export MODULAR_HOME="$HOME/.modular"
    else
        new_path="${HOME}/.tenka/envs/base/pkg/packages.modular.com_mojo/bin"
        new_env_version=$(python -c "
import os 
import json
with open(os.path.expanduser('~/.tenka/environments.json'), 'r') as f:
    envs = json.load(f)
    if 'base' in envs:
        print(envs['base']['version'], end='')
    else:
        print('', end='')
")
        export TENKA_ACTIVE_ENV="base"
        export TENKA_ACTIVE_VERSION="$new_env_version"
        export MODULAR_HOME="$HOME/.tenka/envs/base"
    fi
    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$active_env$|$new_path|" | paste -sd: -)
    echo "Environment '$current_env_name' deactivated"
}

tenka_cli() {
    command="$1"
    case "$command" in
        "" | "-h" | "--help" )
            echo
            echo "*** \e[96mTenka - Mojo Package Manager\e[0m ***"
            echo
            echo "\e[1mUsage:\e[0m \e[96mtenka \e[0m\e[3m<command>\e[0m \e[4m[<args>]\e[0m"
            echo
            echo -e "\e[1mSome useful tenka commands are:\e[0m"
            echo "------------------------------------------"
            echo -e "   \e[1m COMMANDS \e[0m    \e[92mDESCRIPTION\e[0m"
            echo "------------------------------------------"
            echo -e "   \e[1mcreate\e[0m        \e[92mCreate an environment\e[0m"
            echo -e "   \e[1mdelete\e[0m        \e[92mDelete an environment\e[0m"
            echo -e "   \e[1mactivate\e[0m      \e[92mActivate an environment\e[0m"
            echo -e "   \e[1mdeactivate\e[0m    \e[92mDeactivate the current environment\e[0m"
            echo -e "   \e[1msearch\e[0m        \e[92mSearch for packages\e[0m"
            echo -e "   \e[1minstall\e[0m       \e[92mInstall a package in current environment\e[0m"
            echo -e "   \e[1muninstall\e[0m     \e[92mUninstall a package from current environment\e[0m"
            echo -e "   \e[1mpackage\e[0m       \e[92mPackage a mojo file and add it to the current environment\e[0m"
            echo -e "   \e[1mcurrent\e[0m       \e[92mShow the current environment\e[0m"
            echo -e "   \e[1mlist-envs\e[0m     \e[92mList all environments\e[0m"
            echo -e "   \e[1mlist-pkgs\e[0m     \e[92mList all packages\e[0m"
            ;;
        "current")
            shift 1
            if [ -z "$TENKA_ACTIVE_ENV" ] || [ -z "$TENKA_ACTIVE_VERSION" ]; then
                echo "Error: No active Tenka environment found" >&2
                return 1
            fi
            echo "ACTIVE_ENV: $TENKA_ACTIVE_ENV, MOJO VERSION: $TENKA_ACTIVE_VERSION"
            ;;
        "search")
            shift 1
            if ! python3 "$HOME/.tenka/src/main.py" "search" "$@"; then
                echo "Error: Failed to search for packages" >&2
                return 1
            fi
            ;;
        "install")
            shift 1
            if [ -z "$1" ]; then
                echo "Error: Package name not provided" >&2
                return 1
            fi
            package_name="$1"
            branch_name="${2:-main}"
            local active_env="$TENKA_ACTIVE_ENV"
            if [ -z "$active_env" ]; then
                echo "Error: No active Tenka environment found" >&2
                return 1
            fi
            if ! python3 "$HOME/.tenka/src/main.py" "install" "$package_name" "$branch_name" "$active_env"; then
                echo "Error: Failed to install package '$package_name'" >&2
                return 1
            fi
            ;;
        "uninstall")
            shift 1
            if [ -z "$1" ]; then
                echo "Error: Package name not provided" >&2
                return 1
            fi
            package_name="$1"
            local active_env="$TENKA_ACTIVE_ENV"
            if [ -z "$active_env" ]; then
                echo "Error: No active Tenka environment found" >&2
                return 1
            fi
            if ! python3 "$HOME/.tenka/src/main.py" "uninstall" "$package_name" "$active_env"; then
                echo "Error: Failed to uninstall package '$package_name'" >&2
                return 1
            fi
            ;;
  "activate" )
    shift 1
    if ! activate "$@"; then
      echo "Error: Failed to activate environment" >&2
      return 1
    fi
    ;;
  "deactivate" )
    if ! deactivate; then
      echo "Error: Failed to deactivate environment" >&2
      return 1
    fi
    ;;
  "list-pkgs")
    shift 1
    local active_env="$TENKA_ACTIVE_ENV"
    if ! python "$HOME/.tenka/src/main.py" "list-pkgs" "$active_env"; then
      echo "Error: Failed to list packages" >&2
      return 1
    fi
    ;;
  "list-envs")
    shift 1
    if ! python "$HOME/.tenka/src/main.py" "list-envs"; then
      echo "Error: Failed to list environments" >&2
      return 1
    fi
    ;;
  "create" )
    shift 1
    if [ -z "$1" ]; then
      echo "Error: Environment name not provided" >&2
      return 1
    fi
    env_name="$1"
    
    if [ -d "$HOME/.tenka/envs/$env_name" ]; then
        echo "Error: Environment '$env_name' already exists" >&2
        return 1
    fi

    if ! mkdir -p "$HOME/.tenka/envs/$env_name"; then
        echo "Error: Failed to create environment directory" >&2
        return 1
    fi

    latest_version=$(python "$HOME/.tenka/src/packages.py" "get_latest_version")
    if [[ $latest_version == Error:* ]] || [[ $latest_version == "No versions found" ]] || [[ $latest_version == "Unexpected error:"* ]]; then
        echo "Error: Failed to get latest version: $latest_version" >&2
        return 1
    fi
    version="${2:-$latest_version}"
    base_env_path="$HOME/.tenka/envs/base"
    new_env_path="$HOME/.tenka/envs/$env_name"
    if ! rsync -a --exclude='pkg' "$base_env_path/" "$new_env_path/"; then
        echo "Error: Failed to copy base environment" >&2
        return 1
    fi
    if ! mkdir -p "$new_env_path/pkg/packages.modular.com_mojo"; then
        echo "Error: Failed to create package directory" >&2
        return 1
    fi
    if ! python "$HOME/.tenka/src/download.py" "$version" "$env_name"; then
        echo "Error: Failed to download Mojo version" >&2
        return 1
    fi

    if ! python -c "
import os

def change_cfg(env_name, version):
    cfg_path = os.path.expanduser(f'~/.tenka/envs/{env_name}/modular.cfg')
    try:
        with open(cfg_path, 'r') as cfg:
            lines = cfg.readlines()
        
        for i, line in enumerate(lines):
            if line.strip().startswith('version = '):
                lines[i] = f'version = {version}\n'
        
        with open(cfg_path, 'w') as cfg:
            cfg.writelines(lines)
    except IOError as e:
        print(f'Error: Failed to update modular.cfg: {e}')
        return False
    return True

if not change_cfg('$env_name', '$version'):
    exit(1)
"; then
        echo "Error: Failed to update modular.cfg" >&2
        return 1
    fi

    python "$HOME/.tenka/src/environments.py" create_environment "$env_name" "$version"
    echo "Environment '$env_name' created successfully"
    ;;
  "delete" )
    shift 1
    env_name="$1"
    if [ -z "$env_name" ]; then
      echo "Error: Environment name not provided" >&2
      return 1
    fi
    if [[ "$env_name" = "base" ]]; then
      echo "Error: Cannot delete base environment" >&2
      return 1
    fi
    current_env="$TENKA_ACTIVE_ENV"
    if [[ "$current_env" = "$env_name" ]]; then
      echo "Error: Cannot delete active environment" >&2
      return 1
    fi
    python "$HOME/.tenka/src/environments.py" delete_environment "$env_name"
    
    if [[ -d "$HOME/.tenka/envs/$env_name" ]]; then
      if ! rm -rf "$HOME/.tenka/envs/$env_name"; then
        echo "Error: Failed to delete environment directory" >&2
        return 1
      fi
      echo "Environment '$env_name' deleted successfully"
    else
      echo "Warning: Environment directory '$env_name' does not exist, but was removed from configuration" >&2
    fi
    ;;
  "package" )
    shift 1
    local src_name="$1"
    local package_name="$2"
    local package_path="${3:-$(pwd)}"
    local env_name="$TENKA_ACTIVE_ENV"
    if [ -z "$src_name" ] || [ -z "$package_name" ]; then
      echo "Error: Source name and package name must be provided" >&2
      return 1
    fi
    echo "Compiling source - $src_name to $package_name at env: $env_name"
    if ! mojo package "$package_path/$src_name" -o "$HOME/.tenka/envs/$env_name/pkg/packages.modular.com_mojo/lib/mojo/$package_name.mojopkg"; then
      echo "Error: Failed to compile package. Check for version mismatch or errors in the package" >&2
      return 1
    fi
    if ! python "$HOME/.tenka/src/packages.py" "update_package_metadata" "$env_name" "$package_name" "$branch"; then
      echo "Error: Failed to update package metadata" >&2
      return 1
    fi
    echo "Package '$package_name' compiled and added to '$env_name' successfully"
    ;;
  * )
    local command_path="$(command -v "tenka-$command" || true)"
    if [ -z "$command_path" ]; then
      echo "tenka: no such command '$command'" >&2
      return 1
    else
      "$command_path" "$@"
    fi
    ;;
esac
}
