import os
import sys

import click
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from thunder.get_latest import get_latest


def is_root():
    return os.geteuid() == 0

def rerun_as_root(token):
    if not is_root():
        rerun = Confirm.ask("Global installation requires root privileges. Rerun as root?")
        if rerun:
            # Get the original command that was run            
            pythonpath = ':'.join(sys.path)
            cmd = [
                'sudo', 
                'env', 
                f'PATH={os.environ["PATH"]}',
                f'PYTHONPATH={pythonpath}',
                f'TNR_API_TOKEN={token}',
                sys.executable,
            ] + sys.argv
            
            # Replace current process with sudo'd version
            os.execvp('sudo', cmd)

def setup(global_setup, token):
    def check_system_requirements(progress):
        pass
    
    def install_globally(progress):    
        task = progress.add_task("Installing globally...", total=1)
        
        # Check if running as root
        if os.geteuid() != 0:
            progress.update(task, description="❌ Must run as root")
            raise click.ClickException("Global installation requires root privileges")
        
        progress.update(task, description="✅ Running as root")
        
        # Create /etc/thunder directory
        os.makedirs("/etc/thunder", exist_ok=True)
        progress.update(task, description="✅ Created /etc/thunder")
        
        # Create and symlink config file
        sudo_user = os.environ.get('SUDO_USER')
        if not sudo_user:
            progress.update(task, description="❌ SUDO_USER not found")
            raise click.ClickException("Global installation requires sudo")
            
        config_path = "/etc/thunder/config.json"
        libthunder_path = "/etc/thunder/libthunder.so"
            
        user_home = os.path.expanduser(f"~{sudo_user}")
        user_config = os.path.join(user_home, ".thunder", "config.json")
        user_libthunder_path = os.path.join(user_home, ".thunder", "libthunder.so")

        if not os.path.exists(config_path):
            os.symlink(user_config, config_path)
        
        if not os.path.exists(libthunder_path):
            os.symlink(user_libthunder_path, libthunder_path)
        
        # Create a symlink from /etc/libthunder.so to ~/.thunder/libthunder.so
        preload_path = "/etc/ld.so.preload"
        if os.path.exists(preload_path):
            with open(preload_path, "r") as f:
                lines = f.readlines()
            if libthunder_path + '\n' not in lines:
                lines.append(libthunder_path + "\n")
        else:
            lines = [libthunder_path + "\n"]
        with open(preload_path, "w") as f:
            f.writelines(lines)
        progress.update(task, advance=1, description="✅ Updated global installation")

    setup_tasks = [check_system_requirements]
    if global_setup:
        if not is_root():
            rerun_as_root(token)
            raise click.ClickException("Global installation requires root privileges")
        else:
            setup_tasks.append(install_globally)
    
    for task in setup_tasks:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            task(progress)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            progress.add_task("🎉 [bold green]Setup completed successfully![/bold green]", total=0)

if __name__ == "__main__":
    cli()
