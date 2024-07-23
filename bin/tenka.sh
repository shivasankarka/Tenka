
activate() {
    env_name="$1"
    if [ -z "$env_name" ]; then
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
            sys.exit(0)  # success
        else:
            sys.exit(1)  # failure

check_env('$env_name')
"

    if [ $? -eq 1 ]; then
        echo "Error: Environment '$env_name' does not exist"
        return 1
    fi

    if echo "$PATH" | grep -q "${HOME}/.modular/pkg/packages.modular.com_mojo/bin"; then
        old_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        current_env_name="mojo"
    else
        active_env_path=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/bin" | head -n 1)
        current_env_name=$(echo "$active_env_path" | sed -n 's|.*/envs/\([^/]*\)/bin|\1|p')
        old_path="${active_env_path}"
    fi

    new_path="${HOME}/.tenka/envs/${env_name}/bin"
    if [ ! -d "$new_path" ]; then
        echo "Error: Environment '$env_name' does not exist"
        return 1
    fi

    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$old_path$|$new_path|" | paste -sd: -)
    
    if [ "$current_env_name" = "mojo" ]; then
        python "$HOME/.tenka/src/environments.py" change_cfg "mojo" "$env_name"
    else
        python "$HOME/.tenka/src/environments.py" change_cfg "$current_env_name" "$env_name"
    fi
  
    
python -c "
import os
import json

with open(os.path.expanduser('~/.tenka/active.json'), 'w+') as f:
    json.dump({'active': '$env_name'}, f)
"
  
    echo "Environment '$env_name' activated"
}

deactivate() {
    # Find the active environment by searching for a path that matches the format
    active_env=$(echo "$PATH" | tr ':' '\n' | grep "${HOME}/.tenka/envs/[^/]*/bin" | head -n 1)
    
    if [ -z "$active_env" ]; then
        echo "No active Tenka environment found"
        return 1
    fi

    current_env_name=$(echo "$active_env" | sed -n 's|.*/envs/\([^/]*\)/bin|\1|p')
    if [ "$current_env_name" = "base" ]; then
        new_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        python "$HOME/.tenka/src/environments.py" change_cfg "base" "mojo"
        python "$HOME/.tenka/src/environments.py" change_active_env "mojo"
    else
        new_path="${HOME}/.tenka/envs/base/bin"
        python "$HOME/.tenka/src/environments.py" change_cfg "$current_env_name" "base"
        python "$HOME/.tenka/src/environments.py" change_active_env "base"
    fi

    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$active_env$|$new_path|" | paste -sd: -)
    echo "Environment '$current_env_name' deactivated"
}

tenka_cli() {
command="$1"
case "$command" in
  "" | "-h" | "--help" )
    # python3 "$HOME/.tenka/src/main.py" "--help"
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
    ;;
  "current")
    shift 1
    python3 "$HOME/.tenka/src/environments.py" get_active_environment
    ;;
  "search")
    shift 1
    python3 "$HOME/.tenka/src/main.py" "search" "$@"
    ;;
  "install" | "uninstall" )
    shift 1
    python3 "$HOME/.tenka/src/main.py" "$@"
    ;;
  "activate" )
    shift 1
    activate "$@"
    ;;
  "deactivate" )
    deactivate
    ;;
  "create" )
    shift 1
    env_name="$@"
    if [ -d ~/.tenka/envs/"$env_name" ]; then
        echo "Error: Environment already exists"
    else
        mkdir -p ~/.tenka/envs/"$env_name"
    fi
    base_path=~/.tenka/envs/base
    new_env_path=~/.tenka/envs/"$env_name"
    rsync -a "$base_path/" "$new_env_path/"
    python "$HOME/.tenka/src/environments.py" create_environment "$env_name"
    if [ $? -eq 1 ]; then
        echo "Environment '$env_name' created successfully"
    else
        echo "Error: Environment already exists"
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
    echo "compiling $src_name" to "$package_name" at env "$env_name"  
    echo "Active environment: $env_name"
    mojo package "$package_path/$src_name" -o "$HOME/.tenka/envs/$env_name/lib/mojo/$package_name.mojopkg"
    ;;
  "delete" )
    shift 1
    env_name="$@"
    python "$HOME/.tenka/src/environments.py" delete_environment "$env_name"
    if [ $? -eq 1 ]; then
        echo "Environment '$env_name' deleted successfully"
    else
        echo "Error: Environment does not exist"
    fi
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
