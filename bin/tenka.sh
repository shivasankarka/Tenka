# set -e

# TENKA_ROOT="$(cd "$(dirname "$0")/" && pwd)"
# echo "TENKA_ROOT: ${TENKA_ROOT}"
# ENV_NAME="tenka"
# PS1="($ENV_NAME) $PS1"

# python "${TENKA_ROOT}/tenka/main.py"
# echo "Original PATH: $PATH"

# Define old and new paths

# Updated PATH
# echo "Updated PATH: $PATH"
# if [ -z "$OLD_PS1" ]; then
#     export OLD_PS1="$PS1"
# fi

activate() {
    env_name="$1"
    if [ -z "$env_name" ]; then
        echo "Error: Environment name not provided"
        return 1
    fi
    
    # Run the Python script to check if the environment exists
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
        old_path="${HOME}/.tenka/envs/base/bin"
        current_env_name="base"
    fi

    new_path="${HOME}/.tenka/envs/${env_name}/bin"
    # Check if the environment exists
    if [ ! -d "$new_path" ]; then
        echo "Error: Environment '$env_name' does not exist"
        return 1
    fi

    # Replace the old path with the new path
    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$old_path$|$new_path|" | paste -sd: -)
    
    # python "$HOME/.tenka/src/environments.py" change_cfg "base" "$env_name"
    if [ "$current_env_name" = "mojo" ]; then
        python "$HOME/.tenka/src/environments.py" change_cfg "mojo" "$env_name"
    else
        python "$HOME/.tenka/src/environments.py" change_cfg "base" "$env_name"
    fi
    
    # Change the prompt to reflect the current environment
    # export PS1="($env_name) $PS1"
    # echo "PS1: $PS1"
    
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

    env_name=$(echo "$active_env" | sed -n 's|.*/envs/\([^/]*\)/bin|\1|p')
    if [ "$env_name" = "base" ]; then
        new_path="${HOME}/.modular/pkg/packages.modular.com_mojo/bin"
        python "$HOME/.tenka/src/environments.py" change_cfg "$env_name" "mojo"
    else
        new_path="${HOME}/.tenka/envs/base/bin"
        python "$HOME/.tenka/src/environments.py" change_cfg "$env_name" "base"
    fi

    # Replace the active environment path with the default Mojo path if it is "base"
    export PATH=$(echo "$PATH" | tr ':' '\n' | sed "s|^$active_env$|$new_path|" | paste -sd: -)
    # export PS1="$OLD_PS1"
    echo "Environment '$env_name' deactivated"
}

tenka_cli() {
command="$1"
case "$command" in
  "" | "-h" | "--help" )
    echo "Usage: tenka <command> [<args>]"
    echo
    echo "Some useful tenka commands are:"
    echo "   create        Create a new Mojo environment"
    echo "   delete        Delete a Mojo environment"
    echo "   activate      Activate a Mojo environment"
    echo "   deactivate    Deactivate the current Mojo environment"
    echo "   search        Search for packages"
    echo "   install       Install a package"
    echo "   uninstall     Uninstall a package"
    ;;
  "search" | "install" | "uninstall" )
    shift 1
    python3 -c "from tenka.package_manager import $command; $command('$@')"
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
    mkdir -p ~/.tenka/envs/"$env_name"
    base_path=~/.tenka/envs/base
    new_env_path=~/.tenka/envs/"$env_name"
    # cp -r "$base_path" "$new_env_path"
    rsync -a "$base_path/" "$new_env_path/"
    python "$HOME/.tenka/src/environments.py" create_environment "$env_name"
    if [ $? -eq 1 ]; then
        echo "Environment '$env_name' created successfully"
    else
        echo "Error: Environment already exists"
    fi
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
    if [ -z "$command_path" ]; then
      echo "tenka: no such command '$command'" >&2
      # exit 1
    fi

    shift 1
    exec "$command_path" "$@"
    ;;
esac
}

# tenka_cli "$@"