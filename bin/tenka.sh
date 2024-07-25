
activate() {
    new_env_name="$1"
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
        echo "Error: Environment '$env_name' does not exist"
        return 1
    fi

    if echo "$PATH" | grep -q "${HOME}/.modular/pkg/packages.modular.com_mojo/bin"; then
        current_env_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        current_env_name="mojo"
    else
        current_env_path=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/pkg/packages.modular.com_mojo/bin" | head -n 1)
        current_env_name=$(echo "$current_env_path" | sed -n 's|.*/envs/\([^/]*\)/pkg/packages.modular.com_mojo/bin|\1|p')
    fi

    new_path="${HOME}/.tenka/envs/${new_env_name}/pkg/packages.modular.com_mojo/bin"
    if [ ! -d "$new_path" ]; then
        echo "Error: Environment '$new_env_name' does not exist"
        return 1
    fi

new_env_version=$(python -c "
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
  
python -c "
import os
import json


with open(os.path.expanduser('~/.tenka/active.json'), 'w+') as f:
    json.dump({'active': '$new_env_name', 'version': '$new_env_version'}, f)
"
    echo "Environment '$new_env_name' activated"
}

deactivate() {
    active_env=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/pkg/packages.modular.com_mojo/bin" | head -n 1)
    echo "active_env: $active_env"
    if [ -z "$active_env" ]; then
        echo "No active Tenka environment found"
        return 1
    fi

    current_env_name=$(echo "$active_env" | sed -n 's|.*/envs/\([^/]*\)/pkg/packages.modular.com_mojo/bin|\1|p')
    echo "current_env_name: $current_env_name"
    if [ "$current_env_name" = "base" ]; then
        new_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        python "$HOME/.tenka/src/environments.py" change_active_env "mojo"
        export MODULAR_HOME="$HOME/.modular"
    else
        new_path="${HOME}/.tenka/envs/base/pkg/packages.modular.com_mojo/bin"
        python "$HOME/.tenka/src/environments.py" change_active_env "base"
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
    echo -e "   \e[1mlist-envs\e[0m       \e[92mList all environments\e[0m"
    echo -e "   \e[1mlist-pkgs\e[0m       \e[92mList all packages\e[0m"
    ;;
  "current")
    shift 1
    python3 "$HOME/.tenka/src/environments.py" get_active_environment
    ;;
  "search")
    shift 1
    python3 "$HOME/.tenka/src/main.py" "search" "$@"
    ;;
  "install")
    shift 1
    package_name="$1"
    branch_name="${2:-main}"
    python3 "$HOME/.tenka/src/main.py" "install" "$package_name" "$branch_name"
    ;;
  "uninstall")
    shift 1
    package_name="$1"
    python3 "$HOME/.tenka/src/main.py" "uninstall" "$package_name"
    ;;
  "activate" )
    shift 1
    activate "$@"
    ;;
  "deactivate" )
    deactivate
    ;;
  "list-pkgs")
    shift 1
    python "$HOME/.tenka/src/main.py" "list-pkgs"
    ;;
  "list-envs")
    shift 1
    python "$HOME/.tenka/src/main.py" "list-envs"
    ;;
  "create" )
    shift 1
    if [ -z "$1" ]; then
      echo "Error: Environment name not provided"
      return 1
    fi
    env_name="$1"
    
    if [ -d ~/.tenka/envs/"$env_name" ]; then
        echo "Error: Environment already exists"
        return 1
    else
        mkdir -p ~/.tenka/envs/"$env_name"
    fi

    latest_version=$(python "$HOME/.tenka/src/packages.py" "get_latest_version")
    if [[ $latest_version == Error:* ]] || [[ $latest_version == "No versions found" ]] || [[ $latest_version == "Unexpected error:"* ]]; then
        echo "Failed to get latest version: $latest_version"
        exit 1
    fi
    version="${2:-$latest_version}"
    base_env_path=$HOME/.tenka/envs/base
    new_env_path=$HOME/.tenka/envs/"$env_name"
    rsync -a --exclude='pkg' "$base_env_path/" "$new_env_path/"
    mkdir -p "$new_env_path/pkg"
    mkdir -p "$new_env_path/pkg/packages.modular.com_mojo"
    python "$HOME/.tenka/src/download.py" "$version" "$env_name"

python -c "
import os 
import json
import sys

def change_cfg(env_name, version):
  with open(os.path.expanduser('~/.tenka/envs/'+env_name+'/modular.cfg'), 'r+') as cfg:
      content = cfg.read()
      content = content.replace('version = "24.4.0"', f'version = "{version}"')
      cfg.seek(0)
      cfg.write(content)
      cfg.truncate()

change_cfg('$env_name', '$version')
"
    python "$HOME/.tenka/src/environments.py" create_environment "$env_name" "$version"    
    if [ $? -eq 1 ]; then
        echo "Environment '$env_name' created successfully"
    else
        echo "Error: Environment already exists"
    fi
    ;;
  "delete" )
    shift 1
    env_name="$@"
    if [ "$env_name" == "base" ]; then
        echo "Error: Cannot delete base environment"
        return 1
    fi
    python "$HOME/.tenka/src/environments.py" delete_environment "$env_name"
    if [ -d $HOME/.tenka/envs/"$env_name" ]; then
        rm -rf $HOME/.tenka/envs/"$env_name"
        echo "Environment '$env_name' deleted successfully"
    else
        echo "Error: Environment '$env_name' does not exist"
    fi
    ;;
  "package" )
    shift 1
    src_name="$1"
    shift 1
    package_name="$1"
    shift 1
    package_path="$1"
    if [ -z "$package_path" ]; then
        package_path="$(pwd)"
    fi
    env_name="$(python "$HOME/.tenka/src/environments.py" get_active_environment)" || {
        echo "Error: No active environment found"
        return 1
    }
    echo "compiling source - $src_name" to "$package_name" at env: "$env_name"  
    if ! mojo package "$package_path/$src_name" -o "$HOME/.tenka/envs/$env_name/pkg/packages.modular.com_mojo/lib/mojo/$package_name.mojopkg"; then
        echo "Error: There is either a mismatch with the installed Mojo version and package version or errors in the package"
        return 1
    fi
    python "$HOME/.tenka/src/packages.py" "update_package_metadata" "$env_name" "$package_name" "$branch"
    echo "Package '$package_name' compiled and added to '$env_name' successfully"
    ;;
  * )
    command_path="$(command -v "tenka-$command" || true)"
    echo "command_path: $command_path"
    if [ -z "$command_path" ]; then
      echo "tenka: no such command '$command'" >&2
      return 1  
    else
      "$command_path" "$@"  
    fi
    ;;
esac
}
