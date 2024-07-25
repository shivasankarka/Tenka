# setup.py
import os
import json
import datetime
import shutil
import subprocess

def setup_tenka(modular_home: str = "~/.modular"):
    """
    Setup Tenka package manager
    """
    home = os.path.expanduser("~")
    home_dir = os.path.join(home, ".tenka")
    os.makedirs(home_dir, exist_ok=True)
    os.makedirs(os.path.join(home_dir, "envs"), exist_ok=True)

    os.makedirs(os.path.join(home_dir, "bin"), exist_ok=True)
    current_dir_bin = os.path.join(os.getcwd(), "bin")
    destination_dir = os.path.join(home_dir, "bin")
    for item in os.listdir(current_dir_bin):
        item_path = os.path.join(current_dir_bin, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, destination_dir)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(destination_dir, item), dirs_exist_ok=True)

    os.makedirs(os.path.join(home_dir, "src"), exist_ok=True)
    current_dir_src = os.path.join(os.getcwd(), "src")
    destination_dir = os.path.join(home_dir, "src")
    for item in os.listdir(current_dir_src):
        item_path = os.path.join(current_dir_src, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, destination_dir)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(destination_dir, item), dirs_exist_ok=True)

    os.makedirs(os.path.join(home_dir, "envs", "base"), exist_ok=True)
    
    config = {
            'Tenka': {
                'version': 'v0.1',
                'home': '~/.tenka/',
                'modular-installed': False,
                'mojo-installed': False
            }
    }
    modular_installed = subprocess.run(["which", "modular"], capture_output=True, text=True).returncode == 0
    if modular_installed:
        config['Tenka']['modular-installed'] = True
    mojo_installed = subprocess.run(["which", "mojo"], capture_output=True, text=True).returncode == 0
    if mojo_installed:
        config['Tenka']['mojo-installed'] = True       
    with open(os.path.join(home_dir, "config.json"), "w+") as file:
        json.dump(config, file, indent=4)
        
    with open(os.path.expanduser(os.path.join(modular_home, "modular.cfg")), "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("version =") or line.startswith("version="):
                modular_version = line.split("=")[1].strip()
    
    envs = {'base': {'name': 'base', 'version': modular_version, 'description': f'Base environment with Mojo {modular_version}', 'created': datetime.datetime.now().isoformat(), 'packages': []}}
    if not os.path.exists(os.path.join(home_dir, "environments.json")):
        with open(os.path.join(home_dir, "environments.json"), "w") as file:
            json.dump(envs, file, indent=4)        

    active_envs = {'active': 'base', 'version': modular_version}
    if not os.path.exists(os.path.join(home_dir, "active.json")):
        with open(os.path.join(home_dir, "active.json"), "w") as file:
            json.dump(active_envs, file, indent=4)
            
    modular_dir = os.path.expanduser(modular_home)
    tenka_home  = os.path.join(home_dir, "envs", "base")
    for item in os.listdir(modular_dir):
        item_path = os.path.join(modular_dir, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, tenka_home)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(tenka_home, item), dirs_exist_ok=True, symlinks=True)
        
    with open(os.path.join(home_dir, "envs", "base", "modular.cfg"), "r+") as file:
        content = file.read()
        content = content.replace(os.path.expanduser("~/.modular"), os.path.join(home_dir, "envs", "base"))
        file.seek(0)
        file.write(content)
        file.truncate()
   
    with open(os.path.join(home, ".zshrc"), "r") as zshrc:
        lines = zshrc.readlines()
        tenka_lines = ['# Tenka Package Manager\n']
        if not any(line.strip() == tenka_lines[0].strip() for line in lines):
            with open(os.path.join(home, ".zshrc"), "a") as zshrc:
                zshrc.write("\n# Tenka Package Manager\n")
                zshrc.write('''tenka () {
    source $HOME/.tenka/bin/tenka.sh
    tenka_cli "$@"
}
''')
                zshrc.write(f'export MODULAR_HOME="{os.path.expanduser(os.path.join(home_dir, "envs", "base"))}"\n')
                zshrc.write(f'export PATH="{os.path.expanduser(os.path.join(home_dir, "envs", "base", "pkg", "packages.modular.com_mojo", "bin"))}:$PATH"\n')
                
    from colorama import Fore, Style, init
    init(autoreset=True)

    print(f"\n{Fore.YELLOW}{'=' * 50}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'🔥 Tenka 点火':^50}")
    print(f"{Fore.YELLOW}{'=' * 50}\n")

    print(f"{Style.BRIGHT}{Fore.GREEN}✅ Setup Complete!")
    print(f"{Fore.WHITE}To activate Tenka, please do one of the following:")
    print(f"{Fore.YELLOW}  1. {Fore.WHITE}Restart your terminal")
    print(f"{Fore.YELLOW}  2. {Fore.WHITE}Run {Fore.GREEN}'source ~/.zshrc'{Fore.WHITE} in your current session\n")

    print(f"{Fore.CYAN}{Style.BRIGHT}Happy coding, Fellow Mojician! 🪄 🚀\n")
    print(f"{Fore.YELLOW}{'=' * 50}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        setup_tenka(sys.argv[1])
    else:
        setup_tenka()