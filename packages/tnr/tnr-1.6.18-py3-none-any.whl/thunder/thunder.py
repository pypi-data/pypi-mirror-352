import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    import rich_click as click
    import rich
    import asyncio
    import functools # Added for wraps in coro decorator
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.live import Live
    from rich import box
    from thunder import auth
    import os
    import json
    from scp import SCPClient, SCPException
    import paramiko
    from paramiko import ssh_exception
    import subprocess
    import time
    import platform
    from contextlib import contextmanager
    from threading import Timer
    import atexit
    from string import ascii_uppercase
    import socket
    import datetime
    import logging
    from subprocess import Popen
    from logging.handlers import RotatingFileHandler
    import sys
    import sentry_sdk
    from functools import wraps
    import re
    try:
        from importlib.metadata import version
    except Exception as e:
        from importlib_metadata import version

    from thunder import utils
    from thunder.config import Config
    from thunder.get_latest import get_latest
    from thunder import setup_cmd

# Define the coro decorator
def coro(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


def capture_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Get user context for this command execution
            try:
                token = get_token()
                uid = utils.get_uid(token)
                with sentry_sdk.configure_scope() as scope:
                    scope.set_user({"id": uid})
                    scope.set_tag("command", func.__name__)
                    scope.set_context("command_args", {
                        # Skip first arg (click context)
                        "args": args[1:] if args else None,
                        "kwargs": kwargs
                    })
            except Exception:
                # If we can't get the user context, still proceed with command
                pass

            return func(*args, **kwargs)
        except Exception as e:
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            try:
                sentry_sdk.capture_exception(e)
                sentry_sdk.flush()
            finally:
                sys.stdout = old_stdout
            raise
    return wrapper


def handle_click_exception(e):
    """Custom exception handler for Click that sends to Sentry before displaying"""
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    try:
        sentry_sdk.capture_exception(e)
        sentry_sdk.flush()
    finally:
        sys.stdout = old_stdout

    # Use Click's default exception rendering
    click.utils.echo(f"Error: {e.format_message()}", err=True)
    sys.exit(e.exit_code)


# Decorate all command functions with the capture_exception decorator
for attr_name in dir(sys.modules[__name__]):
    attr = getattr(sys.modules[__name__], attr_name)
    if hasattr(attr, '__click_params__'):  # Check if it's a Click command
        setattr(sys.modules[__name__], attr_name, capture_exception(attr))


def get_token():
    global logging_in, DISPLAYED_WARNING

    # Skip token prompt when being used for shell completion
    if '_TNR_COMPLETE' in os.environ:
        return None

    if "TNR_API_TOKEN" in os.environ:
        return os.environ["TNR_API_TOKEN"]

    token_file = auth.get_credentials_file_path()
    if not os.path.exists(token_file):
        logging_in = True
        auth.login()

    with open(auth.get_credentials_file_path(), "r") as f:
        lines = f.readlines()
        if len(lines) == 1:
            token = lines[0].strip()
            return token

    auth.logout()
    logging_in = True
    token = auth.login()
    return token


# Fetch template information at module import
TEMPLATES = utils.get_template_info(get_token())

# Set up template information
sorted_templates = sorted(TEMPLATES, key=lambda t: t['default'], reverse=True)
TEMPLATE_NAMES = [template['name'] if template['default']
                  else template['displayName'] for template in sorted_templates]
NICE_TEMPLATE_NAMES = {
    template['name']: template['displayName'] for template in TEMPLATES}
OPEN_PORTS = {template['name']: template['openPorts']
              for template in TEMPLATES}
AUTOMOUNT_FOLDERS = {
    template['name']: template['automountFolders'] for template in TEMPLATES}
BASE_SPECS = {
    'cores': 4,
    'storage': 100,
    'num_gpus': 1,
    'gpu_type': 'a100'
}

DEFAULT_SPECS = {
    template['name']: template.get('defaultSpecs', BASE_SPECS) for template in TEMPLATES
}

# Set up CLI choices
GPU_CHOICES = ['t4', 'a100', 'a100xl', 'h100']
GPU_MEMORY_MAP = {
    't4': 16,
    'a100': 40,
    'a100xl': 80,
    'h100': 80
}
VCPUS_CHOICES = ['4', '8', '16', '32', '64', '128']
NUM_GPUS_CHOICES = ['1', '2', '4']

# Package information
PACKAGE_NAME = "tnr"
ENABLE_RUN_COMMANDS = True if platform.system() == "Linux" else False
IS_WINDOWS = platform.system() == "Windows"
INSIDE_INSTANCE = False
INSTANCE_ID = None

# Error messages
UNAUTHORIZED_ERROR = "Invalid token, please use `tnr logout` and `tnr login` with a fresh token."

# Remove the DefaultCommandGroup class
DISPLAYED_WARNING = False
logging_in = False

# Completion
CLI_VERSION = version(PACKAGE_NAME)
COMPLETION_DIR = os.path.expanduser('~/.thunder/completions')
PREF_FILE = os.path.expanduser('~/.thunder/autocomplete')
COMPLETION_VERSION_FILE = os.path.expanduser('~/.thunder/completion_version')


@contextmanager
def DelayedProgress(*progress_args, delay=0.1, **progress_kwargs):
    progress = Progress(*progress_args, **progress_kwargs)
    timer = Timer(delay, progress.start)
    timer.start()
    try:
        yield progress
        timer.cancel()
        if progress.live.is_started:
            progress.stop()
    finally:
        timer.cancel()
        if progress.live.is_started:
            progress.stop()

def _generate_completion_script(shell_type, output_file_path, prog_name=PACKAGE_NAME):
    """
    Generates the shell completion script and writes it to the output_file_path.
    """
    try:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        env = os.environ.copy()
        env[f'_{prog_name.upper()}_COMPLETE'] = f'{shell_type}_source'
        
        cmd = [prog_name]
        if getattr(sys, 'frozen', False):
             cmd = [sys.executable]

        process = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True, timeout=10)
        completion_script_content = process.stdout

        with open(output_file_path, 'w') as f:
            f.write(completion_script_content)
        return True
    except FileNotFoundError:
        if not getattr(sys, 'frozen', False) and sys.argv[0] and not prog_name == sys.argv[0]:
            try:
                cmd = [sys.executable, sys.argv[0]]
                process = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True, timeout=10)
                completion_script_content = process.stdout
                with open(output_file_path, 'w') as f:
                    f.write(completion_script_content)
                return True
            except FileNotFoundError:
                pass # Silently fail if fallback not found
            except subprocess.CalledProcessError:
                pass # Silently fail if fallback fails
            except Exception:
                pass # Silently fail on other fallback errors
        return False
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False

def setup_shell_completion(prog_name=PACKAGE_NAME):
    # If this script is being run to generate completion output (triggered by _TNR_COMPLETE env var),
    # then skip trying to set up completions. This prevents recursion when _generate_completion_script
    # calls the tnr command itself.
    # The _TNR_COMPLETE env var is what Click itself uses (based on prog_name).
    # PACKAGE_NAME is 'tnr', so the var becomes '_TNR_COMPLETE'.
    if '_TNR_COMPLETE' in os.environ:
        return

    try:
        if not IS_WINDOWS and hasattr(os, 'geteuid') and os.geteuid() == 0: # Skip for root
            return
    except Exception: # Ignore errors checking UID (e.g. permissions, non-unix)
        pass

    current_cli_version = CLI_VERSION # Use the defined CLI_VERSION

    # Check preference: Has the user already said 'no'?
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, 'r') as f:
                if f.read().strip() == 'no':
                    return
        except IOError: # Problem reading pref file, proceed as if no preference
            pass


    # Detect shell
    shell_type = None
    rc_file_path = None
    completion_file_path = None
    source_line_template = None # For bash/zsh, e.g. 'source "{}"'

    shell_env_var = os.environ.get('SHELL', '').lower()
    
    # Windows: Only support bash via SHELL env var (e.g. Git Bash)
    if IS_WINDOWS:
        if 'bash' in shell_env_var:
            shell_type = 'bash'
            completion_file_path = os.path.join(COMPLETION_DIR, f'{prog_name}-completion.bash')
            rc_file_path = os.path.expanduser('~/.bashrc')
            source_line_template = '[ -f "{}" ] && source "{}"'
    else: # Unix-like
        if 'zsh' in shell_env_var:
            shell_type = 'zsh'
            completion_file_path = os.path.join(COMPLETION_DIR, f'{prog_name}-completion.zsh')
            rc_file_path = os.path.expanduser('~/.zshrc')
            source_line_template = '[ -f "{}" ] && source "{}"'
        elif 'bash' in shell_env_var:
            shell_type = 'bash'
            completion_file_path = os.path.join(COMPLETION_DIR, f'{prog_name}-completion.bash')
            rc_file_path = os.path.expanduser('~/.bashrc')
            source_line_template = '[ -f "{}" ] && source "{}"'
        elif 'fish' in shell_env_var:
            shell_type = 'fish'
            # Fish completions go into a standard directory and are auto-loaded.
            # Ensure the directory structure follows fish conventions.
            fish_completions_dir = os.path.expanduser(f'~/.config/fish/completions')
            completion_file_path = os.path.join(fish_completions_dir, f'{prog_name}.fish')
            # rc_file_path is not for sourcing, but the target file itself for fish.
            # No source_line needed for fish if using this standard path.

    if not shell_type or not completion_file_path:
        return # Unsupported shell or configuration

    # Check if completion script needs generation/regeneration
    needs_generation = False
    if not os.path.exists(completion_file_path):
        needs_generation = True
    elif os.path.exists(COMPLETION_VERSION_FILE):
        try:
            with open(COMPLETION_VERSION_FILE, 'r') as f:
                stored_version = f.read().strip()
            if stored_version != current_cli_version:
                needs_generation = True
        except IOError: # Problem reading version file
            needs_generation = True # Regenerate if version can't be read
    else: # Version file doesn't exist, but completion script does. Regenerate to be sure.
        needs_generation = True

    user_prompted_now = False
    if not os.path.exists(PREF_FILE): # First time or user deleted pref_file
        user_prompted_now = True
        shell_name_display = shell_type.capitalize()
        # Use try-except for click.confirm for environments where it might not be usable (e.g. non-interactive)
        try:
            if click.confirm(f'Enable command completion for {prog_name} ({shell_name_display})?', default=True):
                os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
                with open(PREF_FILE, 'w') as f: f.write('yes')
                needs_generation = True # User just said yes, ensure generation
            else:
                os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
                with open(PREF_FILE, 'w') as f: f.write('no')
                return # User said no
        except Exception: # If click.confirm fails (e.g. non-interactive), default to no setup.
            return


    # Proceed if preference is 'yes' (either pre-existing or just set)
    pref_is_yes = False
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, 'r') as f:
                if f.read().strip() == 'yes':
                    pref_is_yes = True
        except IOError: # Problem reading, treat as not 'yes'
            pass
    
    if not pref_is_yes:
        return

    if needs_generation:
        if _generate_completion_script(shell_type, completion_file_path, prog_name):
            try:
                os.makedirs(os.path.dirname(COMPLETION_VERSION_FILE), exist_ok=True)
                with open(COMPLETION_VERSION_FILE, 'w') as f:
                    f.write(current_cli_version)
            except IOError: # Failed to write version file, completion might be stale next time
                pass # Generation itself succeeded, so continue.
            
            if user_prompted_now: # Only show message on initial successful setup
                 click.echo(f"{prog_name} command completion for {shell_type} has been configured.")
        else:
            # If generation failed, don't try to set up sourcing.
            return

    # For bash and zsh, ensure the rc file sources the completion script
    if shell_type in ['bash', 'zsh'] and rc_file_path and source_line_template:
        new_line_to_add = source_line_template.format(completion_file_path, completion_file_path)
        new_block_with_comment = f'\n# {prog_name} CLI completion\n{new_line_to_add}\n'

        rc_content_original = ""
        try:
            if os.path.exists(rc_file_path):
                with open(rc_file_path, 'r') as f:
                    rc_content_original = f.read()

        except IOError:
            pass # Silently pass if we can't read, will proceed as if empty/no old content
        except Exception:
            return # Do not proceed on unexpected error reading the file

        # Define old patterns to remove
        # These include the common variations of the old dynamic completion setup
        current_shell_env_var_part = "bash_source" if shell_type == 'bash' else "zsh_source"
        old_patterns = [
            # Variations with the 'if command -v ...' block and standard comment
            f'\n# {prog_name} CLI completion\nif command -v {prog_name} >/dev/null 2>&1; then\n  eval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\" > /dev/null 2>&1\nfi\n',
            f'\n# Thunder CLI completion\nif command -v {prog_name} >/dev/null 2>&1; then\n  eval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\" > /dev/null 2>&1\nfi\n',
            # Variations with just the eval line and standard comment
            f'\n# {prog_name} CLI completion\neval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\"\n',
            f'\n# Thunder CLI completion\neval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\"\n',
            # Raw command blocks without specific comments (more generic removal)
            f'if command -v {prog_name} >/dev/null 2>&1; then\n  eval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\" > /dev/null 2>&1\nfi',
            f'eval \"$(_TNR_COMPLETE={current_shell_env_var_part} {prog_name})\"'
        ]
        # Add versions of patterns that might not have a trailing newline if they were at EOF
        old_patterns.extend([p.rstrip('\n') for p in old_patterns[:4]])

        modified_rc_content = rc_content_original
        for pattern in old_patterns:
            modified_rc_content = modified_rc_content.replace(pattern, '')

        # Normalize content: strip whitespace and ensure a single trailing newline if not empty.
        if modified_rc_content.strip():
            modified_rc_content = modified_rc_content.strip() + '\n'
        else:
            modified_rc_content = '' # Ensure it's completely empty if stripping made it so

        # Check if the new sourcing line itself (not the full block with comment) is present
        new_line_is_present = new_line_to_add in modified_rc_content
        
        content_has_changed = modified_rc_content != rc_content_original
        needs_to_add_new_block = not new_line_is_present

        if content_has_changed or needs_to_add_new_block:
            final_content_to_write = modified_rc_content
            if needs_to_add_new_block:
                # Ensure there's a newline before adding our block if content is not empty
                if final_content_to_write and not final_content_to_write.endswith('\n'):
                    final_content_to_write += '\n' 
                final_content_to_write += new_block_with_comment.lstrip('\n') # lstrip to handle if final_content_to_write was empty
            
            try:
                # Write the consolidated changes
                with open(rc_file_path, 'w') as f:
                    f.write(final_content_to_write)
                
                # If we get here, the RC file was modified.
                # Prompt user to restart shell, regardless of whether it was an initial setup or a cleanup.
                if shell_type != 'fish': # Fish doesn't need sourcing from rc/config.fish typically
                    click.echo(f"Your shell configuration file ({rc_file_path}) has been updated.")
                    click.echo(f"Please restart your shell or run: source {rc_file_path}")
                # For fish, the earlier message about configuring is enough if a new file was written.

            except IOError as e:
                # Silently pass if we can't write to the rc file.
                pass 


def init():
    global INSIDE_INSTANCE, INSTANCE_ID, ENABLE_RUN_COMMANDS

    # Skip full initialization when used for shell completion
    if '_TNR_COMPLETE' in os.environ:
        INSIDE_INSTANCE = False
        INSTANCE_ID = None
        return

    try:
        Config().setup(get_token())
        deployment_mode = Config().get("deploymentMode", "public")

        if deployment_mode == "public":
            # Check if we're in an instance based on config.json
            INSTANCE_ID = Config().getX("instanceId")
            if INSTANCE_ID == -1 or INSTANCE_ID is None:
                INSIDE_INSTANCE = False
                INSTANCE_ID = None
            else:
                INSIDE_INSTANCE = True

        elif deployment_mode == "test":
            ENABLE_RUN_COMMANDS = True
            INSTANCE_ID = 0

        else:
            raise click.ClickException(
                f"deploymentMode field in `{Config().file}` is set to an invalid value"
            )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise


init()
# Setup Sentry for error reporting with more context
sentry_sdk.init(
    dsn="https://ba3a63bb837905e030f7184f1ca928d3@o4508006349012992.ingest.us.sentry.io/4508802738683904",
    send_default_pii=True,
    traces_sample_rate=1.0,
    debug=False,
    attach_stacktrace=True,
    shutdown_timeout=0,
    before_send=lambda event, hint: {
        **event,
        'extra': {
            **(event.get('extra', {})),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'inside_instance': INSIDE_INSTANCE,
            'instance_id': INSTANCE_ID,
            'package_version': version(PACKAGE_NAME),
            'deployment_mode': Config().get("deploymentMode", "public") if Config().file else None
        }
    }
)
sentry_sdk.profiler.start_profiler()
try:
    setup_shell_completion()
except Exception as e:
    pass

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.COMMAND_GROUPS = {
    "cli": [
        {
            "name": "Instance management",
            "commands": ["create", "delete", "start", "stop", "modify", "snapshot"],
        },
        {
            "name": "Utility",
            "commands": ["connect", "status", "scp", "update"],
        },
        {
            "name": "Account management",
            "commands": ["login", "logout"],
        },
    ]
}

COLOR = "cyan"
click.rich_click.STYLE_OPTION = COLOR
click.rich_click.STYLE_COMMAND = COLOR
click.exceptions.ClickException.show = handle_click_exception

main_message = (
    f":laptop_computer: [bold {COLOR}]You're in a local environment, use these commands to manage your Thunder Compute instances[/]"
)


class VersionCheckGroup(click.RichGroup):
    def __call__(self, ctx=None, *args, **kwargs):
        meets_min, is_latest, details = utils.check_cli_up_to_date()
        is_binary = getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')
        should_run_command = True  # Assume we run the command unless checks fail

        # --- Handle Mandatory Update ---
        if not meets_min:
            should_run_command = False  # Don't run command if min not met
            click.echo(click.style(
                "Mandatory update required.", fg="red", bold=True))
            error_title = "Error: Minimum Version Not Met"
            error_msg = ""
            update_instruction = ""

            if is_binary:
                expected_hash = details[2] if details and details[0] == 'hash' else None
                if not expected_hash:
                    _, hash_details = utils.check_binary_hash()
                    expected_hash = hash_details[2] if hash_details and hash_details[0] == 'hash' else None

                if not expected_hash:
                    error_msg = f"Your tnr binary is below the minimum required version, but could not determine the hash for update."
                    update_instruction = "Please download the latest version manually from https://console.thundercompute.com/?download"
                else:
                    click.echo(click.style(
                        "Attempting automatic update...", fg="yellow"))
                    update_result = utils.attempt_binary_self_update(
                        expected_hash)

                    if update_result is True or update_result == 'pending_restart':
                        sys.exit(0)
                    else:  # Auto-update failed
                        error_msg = f"Your tnr binary is below the minimum version.\nAutomatic update failed."
                        update_instruction = "Please download the latest version from https://console.thundercompute.com/?download"

            else:  # Pip install
                if details and details[0] == 'version':
                    _, current_version, required_version = details
                    error_msg = f'Your tnr version ({current_version}) is outdated. Minimum required version is {required_version}.'
                else:
                    error_msg = "Your tnr version is below the minimum required version."
                update_instruction = 'Please run "pip install --upgrade tnr" to update.'

            # Display error panel for mandatory update failure
            full_message = f"{error_msg}\n{update_instruction}"
            panel = Panel(full_message, title=error_title,
                          style="white", border_style="red", width=80)
            Console().print(panel)
            sys.exit(1)

        # --- Handle Optional Update ---
        elif not is_latest:
            if is_binary and details and details[0] == 'hash':
                last_attempt_time = utils.read_optional_update_cache()
                if time.time() - last_attempt_time > utils.OPTIONAL_UPDATE_CACHE_TTL:
                    should_run_command = False  # Don't run command after attempting optional update
                    click.echo(click.style(
                        "Automatically updating to the latest version of tnr. Please wait...", fg="cyan"))
                    _, current_hash, expected_hash = details
                    update_result = utils.attempt_binary_self_update(
                        expected_hash)
                    utils.write_optional_update_cache()  # Record this attempt time

                    if update_result is True or update_result == 'pending_restart':
                        click.echo(click.style(
                            "Update finished! You can now re-run your command.", fg="green"))
                    elif update_result is False:
                        warning_title = "Warning: Optional Background Update Failed"
                        warning_msg = (
                            f'Failed to automatically update tnr in the background.\n'
                            f'  Current hash:  {current_hash[:12]}...\n'
                            f'  Expected hash: {expected_hash[:12]}...\n'
                            f'You can download the latest from https://console.thundercompute.com/?download'
                        )
                        panel = Panel(warning_msg, title=warning_title,
                                      style="white", border_style="yellow", width=80)
                        Console().print(panel)

                    # Always exit after attempting an optional update, prompting user to re-run
                    sys.exit(0)
                # else: # Optional update skipped due to cache - allow command to run
            # else: # Not a binary hash mismatch - allow command to run

        # --- Proceed only if no blocking update occurred ---
        if should_run_command:
            # Prevent execution inside instance (always checked before running)
            if INSIDE_INSTANCE:
                error_msg = "The 'tnr' command line tool is not available inside Thunder Compute instances."
                panel = Panel(error_msg, title="Error",
                              style="white", border_style="red", width=80)
                Console().print(panel)
                sys.exit(1)

            # Execute the command
            return super().__call__(ctx, *args, **kwargs)
        else:
            # This case should theoretically not be reached if exits are handled above,
            # but adding a safety exit just in case.
            sys.exit(1)


@click.group(
    cls=VersionCheckGroup,
    help=main_message,
    context_settings={"ignore_unknown_options": True,
                      "allow_extra_args": True},
)
@click.version_option(version=version(PACKAGE_NAME))
def cli():
    # utils.validate_config()
    pass


if ENABLE_RUN_COMMANDS:

    @cli.command(
        help="Runs process on a remote Thunder Compute GPU. The GPU type is specified in the ~/.thunder/dev file. For more details, please go to thundercompute.com",
        context_settings={"ignore_unknown_options": True,
                          "allow_extra_args": True},
        hidden=True,
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    @click.option("--nowarnings", is_flag=True, help="Hide warning messages")
    def run(args, nowarnings):
        if not args:
            raise click.ClickException("No arguments provided. Exiting...")

        token = get_token()
        uid = utils.get_uid(token)

        # Run the requested process
        if not INSIDE_INSTANCE and not nowarnings:
            message = "[yellow]Attaching to a remote GPU from a non-managed instance - this will hurt performance. If this is not intentional, please connect to a managed CPU instance using tnr create and tnr connect <INSTANCE ID>[/yellow]"
            panel = Panel(
                message,
                title=":warning:  Warning :warning: ",
                title_align="left",
                highlight=True,
                width=100,
                box=box.ROUNDED,
            )
            rich.print(panel)

        # config = utils.read_config()
        if Config().contains("binary"):
            binary = Config().get("binary")
            if not os.path.isfile(binary):
                raise click.ClickException(
                    "Invalid path to libthunder.so in config.binary"
                )
        else:
            binary = get_latest("client", "~/.thunder/libthunder.so")
            if binary == None:
                raise click.ClickException("Failed to download binary")

        device = Config().get("gpuType", "t4")
        if device.lower() != "cpu":
            os.environ["LD_PRELOAD"] = f"{binary}"

        # This should never return
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            raise click.ClickException(
                f"Invalid command: \"{' '.join(args)}\"")
        except Exception as e:
            raise click.ClickException(f"Unknown exception: {e}")

    @cli.command(
        help="View or change the GPU configuration for this instance. Run without arguments to see current GPU and available options.",
        hidden=not INSIDE_INSTANCE,
    )
    @click.argument("gpu_type", required=False)
    @click.option("-n", "--ngpus", type=int, help="Number of GPUs to request (default: 1). Multiple GPUs increase costs proportionally")
    @click.option("--raw", is_flag=True, help="Output device name and number of devices as an unformatted string")
    def device(gpu_type, ngpus, raw):
        # config = utils.read_config()
        supported_devices = set(
            [
                "cpu",
                "t4",
                "v100",
                "a100",
                "a100xl",
                "l4",
                "p4",
                "p100",
                "h100",
            ]
        )

        if gpu_type is None:
            # User wants to read current device
            device = Config().get("gpuType", "t4")
            gpu_count = Config().get("gpuCount", 1)

            if raw is not None and raw:
                if gpu_count <= 1:
                    click.echo(device.upper())
                else:
                    click.echo(f"{gpu_count}x{device.upper()}")
                return

            if device.lower() == "cpu":
                click.echo(
                    click.style(
                        "📖 No GPU selected - use `tnr device <gpu-type>` to select a GPU",
                        fg="white",
                    )
                )
                return

            console = Console()
            if gpu_count == 1:
                console.print(
                    f"[bold green]📖 Current GPU:[/] {device.upper()}")
            else:
                console.print(
                    f"[bold green]📖 Current GPUs:[/][white] {gpu_count} x {device.upper()}[/]"
                )

            utils.display_available_gpus()
            return

        if gpu_type.lower() not in supported_devices:
            raise click.ClickException(
                f"Unsupported device type: {gpu_type}. Please use tnr device (without arguments) to view available devices."
            )

        if ngpus is not None and ngpus < 1:
            raise click.ClickException(
                f"Unsupported device count {ngpus} - must be at least 1"
            )

        if gpu_type.lower() == "cpu":
            Config().set("gpuType", "cpu")
            Config().set("gpuCount", 0)

            click.echo(
                click.style(
                    f"✅ Device set to CPU, your instance does not have access to GPUs.",
                    fg="green",
                )
            )
        else:
            Config().set("gpuType", gpu_type.lower())

            gpu_count = ngpus if ngpus is not None else 1
            Config().set("gpuCount", gpu_count)
            click.echo(
                click.style(
                    f"✅ Device set to {gpu_count} x {gpu_type.upper()}", fg="green"
                )
            )
        Config().save()

    @cli.command(
        help="Activate a tnr shell environment. Anything that you run in this shell has access to GPUs through Thunder Compute",
        hidden=True,
    )
    def activate():
        if INSIDE_INSTANCE:
            raise click.ClickException(
                "The 'tnr' command line tool is not available inside Thunder Compute instances."
            )
        pass

    @cli.command(
        help="Deactivate a tnr shell environment. Your shell will no longer have access to GPUs through Thunder Compute",
        hidden=True,
    )
    def deactivate():
        if INSIDE_INSTANCE:
            raise click.ClickException(
                "The 'tnr' command line tool is not available inside Thunder Compute instances."
            )
        pass

# else:

    # @cli.command(hidden=True)
    # @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    # def run(args):
    #     raise click.ClickException(
    #         "tnr run is supported within Thunder Compute instances. Create one with 'tnr create' and connect to it using 'tnr connect <INSTANCE ID>'"
    #     )

    # @cli.command(hidden=True)
    # @click.argument("gpu_type", required=False)
    # @click.option("-n", "--ngpus", type=int, help="Number of GPUs to use")
    # @click.option("--raw", is_flag=True, help="Output raw device information")
    # def device(gpu_type, ngpus, raw):
    #     raise click.ClickException(
    #         "tnr device is supported within Thunder Compute instances. Create one with 'tnr create' and connect to it using 'tnr connect <INSTANCE ID>'"
    #     )


@cli.command(hidden=True)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def launch(args):
    return run(args)


if INSIDE_INSTANCE:
    @cli.command(
        help="Display status and details of all your Thunder Compute instances, including running state, IP address, hardware configuration, and resource usage"
    )
    def status():
        with DelayedProgress(
            SpinnerColumn(spinner_name="dots", style="white"),
            TextColumn("[white]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task(
                "Loading", total=None)  # No description text

            token = get_token()

        # Retrieve IP address and active sessions in one call
            current_ip, active_sessions = utils.get_active_sessions(token)

            # Extract storage information
            storage_total = (
                subprocess.check_output(
                    "df -h / | awk 'NR==2 {print $2}'", shell=True)
                .decode()
                .strip()
            )
            storage_used = (
                subprocess.check_output(
                    "df -h / | awk 'NR==2 {print $3}'", shell=True)
                .decode()
                .strip()
            )

            disk_space_text = Text(
                f"Disk Space: {storage_used} / {storage_total} (Used / Total)",
                style="white"
            )

            # Format INSTANCE_ID and current_ip as Text objects with a specific color (e.g., white)
            instance_id_text = Text(f"ID: {INSTANCE_ID}", style="white")
            current_ip_text = Text(f"Public IP: {current_ip}", style="white")

        # Console output for instance details
        console = Console()
        console.print(Text("Instance Details", style="bold green"))
        console.print(instance_id_text)
        console.print(current_ip_text)
        console.print(disk_space_text)
        console.print()

        # GPU Processes Table
        gpus_table = Table(
            title="Active GPU Processes",
            title_style="bold green",
            title_justify="left",
            box=box.ROUNDED,
        )

        gpus_table.add_column("GPU Type", justify="center")
        gpus_table.add_column("Duration", justify="center")

        # Populate table with active sessions data
        for session_info in active_sessions:
            gpus_table.add_row(
                f'{session_info["count"]} x {session_info["gpu"]}',
                f'{session_info["duration"]}s',
            )

        # If no active sessions, display placeholder
        if not active_sessions:
            gpus_table.add_row("--", "--")

        # Print table
        console.print(gpus_table)

else:

    @cli.command(help="List details of Thunder Compute instances within your account")
    @click.option('--no-wait', is_flag=True, help="Don't wait for status updates")
    def status(no_wait):
        def get_table(instances, show_timestamp=False, changed=False, loading=False):
            instances_table = Table(
                title="Thunder Compute Instances",
                title_style="bold cyan",
                title_justify="left",
                box=box.ROUNDED,
            )

            instances_table.add_column("ID", justify="center")
            instances_table.add_column("Status", justify="center")
            instances_table.add_column("Address", justify="center")
            instances_table.add_column("Disk", justify="center")
            instances_table.add_column("GPU", justify="center")
            instances_table.add_column("vCPUs", justify="center")
            instances_table.add_column("RAM", justify="center")
            instances_table.add_column("Template", justify="center")

            if loading:
                instances_table.add_row(
                    "...",
                    Text("LOADING", style="cyan"),
                    "...",
                    "...",
                    "...",
                    "...",
                    "...",
                    "..."
                )
            else:
                for instance_id, metadata in instances.items():
                    if metadata["status"] == "RUNNING":
                        status_color = "green"
                    elif metadata["status"] == "STOPPED":
                        status_color = "red"
                    else:
                        status_color = "yellow"

                    ip_entry = metadata["ip"] if metadata["ip"] else "--"
                    gpu_count = metadata['numGpus'] if metadata['numGpus'] else '1'
                    gpu_type = metadata['gpuType'].upper(
                    ) if metadata['gpuType'] else "--"
                    gpu_entry = f"{gpu_count}x{gpu_type}" if str(
                        gpu_count) != '1' else gpu_type if gpu_type != "--" else "--"

                    # Determine the template name based on whether it's a standard template or a client snapshot
                    template_key = metadata["template"]
                    if not template_key.startswith("client-image-"):
                        # Standard template: Use display name from NICE_TEMPLATE_NAMES or the key itself if not found
                        template_name = NICE_TEMPLATE_NAMES.get(
                            template_key, template_key)
                    else:
                        # Client snapshot: Try to get display name from TEMPLATES, default to "Deleted Snapshot"
                        for template in TEMPLATES:
                            if template["name"] == template_key:
                                template_name = template["displayName"]
                                break
                            else:
                                template_name = "Deleted Snapshot"

                    instances_table.add_row(
                        str(instance_id),
                        Text(metadata["status"], style=status_color),
                        str(ip_entry),
                        f"{metadata['storage']}GB",
                        str(gpu_entry),
                        str(metadata['cpuCores']),
                        f"{int(metadata['memory'])}GB",
                        template_name,
                    )

                if len(instances) == 0:
                    instances_table.add_row(
                        "--", "--", "--", "--", "--", "--", "--", "--")

            if show_timestamp:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                status = "No instances in pending state! Monitoring stopped." if changed else "Press Ctrl+C to stop monitoring"
                if loading:
                    status = "Loading initial state..."
                instances_table.caption = f"Last updated: {timestamp}\n{status}"

            return instances_table

        def fetch_data(show_progress=True):
            token = get_token()
            success, error, instances = utils.get_instances(
                token, use_cache=False)

            if not success:
                if "Unauthorized" in error:
                    raise click.ClickException(
                        UNAUTHORIZED_ERROR
                    )
                else:
                    raise click.ClickException(
                        f"Status command failed with error: {error}"
                    )
            return instances

        def instances_changed(old_instances, new_instances):
            if old_instances is None:
                return False

            # Compare instance statuses - we can add other stuff here,
            # but figured this would be the most useful
            return (
                any(
                    old_instances[id]["status"] != new_instances[id]["status"]
                    for id in old_instances if id in new_instances
                )
            )

        def in_transition(instances):
            if instances is None:
                return False

            return (
                any(
                    instances[id]["status"] in ["STARTING",
                                                "STOPPING", "PENDING", "STAGING", "PROVISIONING"]
                    for id in instances
                )
            )

        console = Console()

        if not no_wait:
            previous_instances = None
            final_table = None
            initial_table = get_table({}, show_timestamp=True, loading=True)

            try:
                # Provide initial table to Live to show immediately
                with Live(initial_table, refresh_per_second=4, transient=True) as live:
                    # Fetch initial data
                    current_instances = fetch_data(show_progress=False)
                    previous_instances = current_instances
                    while True:
                        table = get_table(current_instances,
                                          show_timestamp=True, changed=False)
                        final_table = table  # Keep track of last state
                        live.update(table)

                        transitioning = in_transition(current_instances)
                        if not transitioning:
                            break  # Exit immediately if no instances are transitioning

                        time.sleep(5)
                        current_instances = fetch_data(show_progress=False)
                        changed = instances_changed(
                            previous_instances, current_instances)
                        transitioning = in_transition(current_instances)
                        # Only break if no instances are transitioning anymore
                        if not transitioning:
                            table = get_table(
                                current_instances, show_timestamp=True, changed=True)
                            final_table = table
                            live.update(table)
                            # Exit the loop if no instances are transitioning
                            break

                        previous_instances = current_instances

            except KeyboardInterrupt:
                pass  # Don't let the command abort - we want to print out the table after

            if final_table:
                console.print(final_table)
        else:
            # Single display mode
            # Show initial loading skeleton in a Live display
            with Live(get_table({}, loading=True), refresh_per_second=4) as live:
                instances = fetch_data(show_progress=False)
                table = get_table(instances)
                live.update(table)

            if len(instances) == 0:
                console.print(
                    "Tip: use `tnr create` to create a Thunder Compute instance")


@cli.command(
    help=f"Create a new Thunder Compute instance. Available templates: {', '.join(TEMPLATE_NAMES)}",
    hidden=INSIDE_INSTANCE,
)
@click.option('--vcpus', type=click.Choice(VCPUS_CHOICES),
              help='Number of vCPUs. Cost scales with vCPU count')
@click.option('--template', type=click.Choice(TEMPLATE_NAMES),
              help=f'Environment template: {", ".join(TEMPLATE_NAMES)}')
@click.option('--gpu', type=click.Choice(GPU_CHOICES),
              help='GPU type: T4 (16GB, inference), A100 (40GB, training), A100XL (80GB, training), H100 (80GB, training)')
@click.option('--num-gpus', type=click.Choice(NUM_GPUS_CHOICES),
              help='Number of GPUs to request (default: 1). Multiple GPUs increase costs proportionally')
@click.option("--disk-size-gb", type=int, default=None, metavar="SIZE_GB", help="Disk size in GB (default: 100, max: 1024)")
def create(vcpus, template, gpu, num_gpus, disk_size_gb):

    # Default values based on template
    default_template = 'base'
    spec_template = template if template else default_template
    default_vcpus = str(DEFAULT_SPECS[spec_template]['cores'])
    default_gpu = DEFAULT_SPECS[spec_template]['gpu_type']
    default_num_gpus = str(DEFAULT_SPECS[spec_template]['num_gpus'])
    default_disk_size_gb = str(DEFAULT_SPECS[spec_template]['storage'])

    # Prompt for values if not provided
    if vcpus is None:
        vcpus = click.prompt(
            f"Number of vCPUs; 4GB RAM per vCPU",
            type=click.Choice(VCPUS_CHOICES),
            default=default_vcpus,
            show_default=True,
            show_choices=True
        )

    if gpu is None:
        gpu = click.prompt(
            "GPU type",
            type=click.Choice(GPU_CHOICES),
            default=default_gpu,
            show_default=True,
            show_choices=True
        )

    if num_gpus is None:
        num_gpus = click.prompt(
            "Number of GPUs",
            type=click.Choice(NUM_GPUS_CHOICES),
            default=default_num_gpus,
            show_default=True,
            show_choices=True
        )

    if template is None:
        template = click.prompt(
            "Template",
            type=click.Choice(TEMPLATE_NAMES),
            default=default_template,
            show_default=True,
            show_choices=True
        )

    if disk_size_gb is None:
        disk_size_gb = click.prompt(
            "Disk size in GB (min: 100, max: 1024)",
            type=int,
            default=default_disk_size_gb,
            show_default=True
        )

    if gpu == 'h100' and int(num_gpus) > 1:
        raise click.ClickException(
            f"❌ We do not currently support multiple H100 GPUs. Please set --num-gpus to 1."
        )

    def memory_error(required_vcpus):
        required_vcpus = int(required_vcpus)
        higher_options = [vcpu for vcpu in [int(vcpu) for vcpu in VCPUS_CHOICES] if vcpu >= required_vcpus]
        return f"❌ This GPU configuration requires at least {min(higher_options)} vCPUs. Please increase the number of vCPUs."
    
    required_vcpus = (GPU_MEMORY_MAP[gpu] * int(num_gpus)) / 10
    if gpu == 'a100xl' and int(num_gpus) == 1 and int(vcpus) == 4:
        pass
    elif int(vcpus) < required_vcpus:
        raise click.ClickException(memory_error(required_vcpus))

    if disk_size_gb > 1024:
        raise click.ClickException(
            f"❌ The requested size ({disk_size_gb}GB) exceeds the 1TB limit."
        )

    if template == 'ollama-llama4':
        if int(vcpus) < 32 or int(disk_size_gb) < 150 or gpu != 'a100xl':
            raise click.ClickException(
                "The ollama-llama4 template requires at least 32 CPU cores, 150GB of storage, and an A100 80GB GPU."
            )

    if template == 'webui-forge' and (gpu == 't4' or int(vcpus) < 8):
        message = "[yellow]The FLUX models pre-loaded onto this template are not supported on T4 GPUs. If your goal is to run FLUX, please use an A100 by setting --gpu a100 or a100xl. It's also recommended to use at least 8 vCPUs.[/yellow]"
        panel = Panel(
            message,
            title=":warning:  Warning :warning: ",
            title_align="left",
            highlight=True,
            width=100,
            box=box.ROUNDED,
        )
        rich.print(panel)
        # Ask user if they want to continue
        if not click.confirm(click.style("Do you want to continue running this template with lower than recommended specifications?", fg="cyan")):
            return

    with DelayedProgress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("Loading", total=None)  # No description text
        token = get_token()
        # Get the template name from display name for custom templates
        for template_data in TEMPLATES:
            if template_data['name'] == template or template_data['displayName'] == template:
                template = template_data['name']
                if not template_data['default'] and disk_size_gb == 100:
                    disk_size_gb = template_data['defaultStorage']
                elif not template_data['default'] and disk_size_gb < template_data['defaultStorage']:
                    raise click.ClickException(
                        f"❌ The requested size ({disk_size_gb}GB) is less than the minimum size ({template_data['defaultStorage']}GB) for this snapshot."
                    )
                break
        success, error, instance_id = utils.create_instance(
            token, vcpus, gpu, template, num_gpus, disk_size_gb
        )

    if success:
        # Attempt to add key to instance right away (optional)
        if not utils.add_key_to_instance(instance_id, token):
            click.echo(click.style(
                f"Warning: Unable to create or attach SSH key for instance {instance_id} immediately. The background config will try again.",
                fg="yellow"
            ))

        start_background_config(instance_id, token)
        click.echo(
            click.style(
                f"Successfully created Thunder Compute instance {instance_id}!\n",
                fg="cyan",
            )
        )

        # Add a short delay before showing status
        time.sleep(0.5)
        ctx = click.get_current_context()
        ctx.invoke(status)
    else:
        if "Unauthorized" in error:
            raise click.ClickException(
                UNAUTHORIZED_ERROR
            )
        elif "is not ready yet" in error:
            raise click.ClickException(
                f"Snapshot is not ready yet. Check the status of the snapshot using `tnr snapshot --list`."
            )
        elif "does not exist" in error:
            raise click.ClickException(
                f"Failed to create Thunder Compute instance as template/snapshot {template} does not exist."
            )
        else:
            raise click.ClickException(
                f"Failed to create Thunder Compute instance: {error}"
            )


@cli.command(
    help="Permanently delete a Thunder Compute instance. This action is not reversible",
    hidden=INSIDE_INSTANCE,
)
@click.argument("instance_id", required=True)
def delete(instance_id):
    with DelayedProgress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("Loading", total=None)  # No description text
        token = get_token()
        _, _, instances = utils.get_instances(token, use_cache=False)
        delete_success, error = utils.delete_instance(instance_id, token)

    if delete_success:
        click.echo(
            click.style(
                f"Successfully deleted Thunder Compute instance {instance_id}",
                fg="cyan",
            )
        )
        utils.remove_instance_from_ssh_config(f"tnr-{instance_id}")
        try:
            device_ip = instances[instance_id]['ip']
            utils.remove_host_key(device_ip)
        except Exception as _:
            pass
    else:
        raise click.ClickException(
            f"Failed to delete Thunder Compute instance {instance_id}: {error}"
        )


def setup_background_logging():
    log_dir = os.path.expanduser("~/.thunder/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "background_config.log")

    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger("thunder_background")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def get_instance_lock_file(instance_id):
    """Get the path to the lockfile for a specific instance."""
    lock_dir = os.path.expanduser("~/.thunder/locks")
    os.makedirs(lock_dir, exist_ok=True)
    return os.path.join(lock_dir, f"instance_{instance_id}.lock")


def write_lock_file(lock_file):
    """Write the current process ID to the lock file."""
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def is_lock_stale(lock_file):
    """Check if the lockfile exists and if the process is still running."""
    try:
        if not os.path.exists(lock_file):
            return False

        with open(lock_file, 'r') as f:
            pid = int(f.read().strip())

        # Check if process exists
        try:
            # Don't actually send a signal, just check if we can
            os.kill(pid, 0)
            return False
        except ProcessLookupError:  # Process doesn't exist
            return True
        # Process exists but we don't have permission (still means it's running)
        except PermissionError:
            return False
    except Exception:
        return True  # If we can't read the file or it's invalid, consider it stale


def check_active_ssh_sessions(ssh):
    """Check if there are any active SSH sessions on the remote host."""
    try:
        # Count SSH processes excluding our current connection and sshd
        # The [s] trick prevents the grep itself from showing up
        # -v grep excludes our check command
        # We look for established connections only
        cmd = "ps aux | grep '[s]sh.*ubuntu@' | grep -v grep | wc -l"
        _, stdout, _ = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            return False
        count = stdout.read().decode().strip()

        try:
            # If we get more than 1 connection (excluding our current one)
            return int(count) > 1
        except ValueError:
            return False
    except Exception:
        return False


def wait_for_background_config(instance_id, timeout=60):
    """Wait for background configuration to complete by checking lockfile."""
    lock_file = get_instance_lock_file(instance_id)
    start_time = time.time()

    while os.path.exists(lock_file):
        if time.time() - start_time > timeout:
            return False
        time.sleep(1)
    return True


def robust_ssh_connect(ip, keyfile, max_wait=120, interval=5, username="ubuntu"):
    """
    Attempt to connect to the given IP using provided keyfile for up to max_wait seconds,
    retrying every 'interval' seconds. Returns an SSHClient on success, or raises an Exception on failure.
    """
    start_time = time.time()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    last_error = None
    connection = None
    socket_test = None
    progress = Progress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    )
    try:
        progress.start()
        task = progress.add_task("Establishing SSH connection...", total=None)

        while time.time() - start_time < max_wait:
            try:
                # First check if we can reach the host
                socket_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_test.settimeout(5)
                try:
                    socket_test.connect((ip, 22))
                except (socket.timeout, socket.error) as e:
                    # If we can't connect to port 22, update progress and retry
                    progress.update(
                        task, description=f"Waiting for instance to be ready...")
                    last_error = f"Network error: {str(e)}"
                    time.sleep(interval)
                    continue
                finally:
                    if socket_test:
                        try:
                            socket_test.close()
                        except:
                            pass

                # Update progress for SSH attempt
                progress.update(
                    task, description="Continuing SSH connection...")

                # Now try SSH connection
                ssh.connect(ip, username=username,
                            key_filename=keyfile, allow_agent=False, look_for_keys=False, timeout=15)
                connection = ssh
                break
            except paramiko.AuthenticationException as e:
                last_error = f"Authentication failed: {str(e)}"
                progress.update(
                    task, description=f"Retrying SSH connection... ({str(e)})")
                time.sleep(interval)
            except paramiko.SSHException as e:
                last_error = f"SSH error: {str(e)}"
                progress.update(
                    task, description=f"Retrying SSH connection... ({str(e)})")
                time.sleep(interval)
            except (socket.timeout, TimeoutError) as e:
                last_error = f"Connection timeout: {str(e)}"
                progress.update(
                    task, description=f"Connection timed out, retrying...")
                time.sleep(interval)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                progress.update(
                    task, description=f"Retrying connection... ({str(e)})")
                time.sleep(interval)

    except Exception as e:
        # Handle any errors from the progress bar itself
        last_error = f"Progress display error: {str(e)}"
    finally:
        # Always ensure progress is stopped
        try:
            progress.stop()
        except:
            pass

        # Clean up SSH connection if needed
        if not connection and ssh:
            try:
                ssh.close()
            except:
                pass

    if connection:
        return connection

    error_msg = f"Failed to establish SSH connection to {ip} within {max_wait} seconds. {last_error} \nPlease try again in a few moments or contact support@thundercompute.com if the issue persists."

    raise click.ClickException(error_msg)


def wait_and_configure_ssh(instance_id, token):
    logger = setup_background_logging()
    logger.info(
        f"Starting background configuration for instance {instance_id}")
    lock_file = get_instance_lock_file(instance_id)
    try:
        max_attempts = 120  # 5 minutes total (60 * 5 seconds)
        max_instance_not_found_attempts = 5
        attempt = 0
        instance_not_found_attempt = 0

        while attempt < max_attempts:
            success, error, instances = utils.get_instances(
                token, use_cache=False)
            if not success:
                logger.error(f"Failed to get instances: {error}")
                return

            if instance_id not in instances:
                logger.error(f"Instance {instance_id} not found")
                # Sometimes GCP does this weird thing where they set a STOPPING of the instance
                # before it actually starts. Going to set a max-retry for this
                instance_not_found_attempt += 1
                if instance_not_found_attempt == max_instance_not_found_attempts:
                    return
                else:
                    time.sleep(1)
                    continue

            instance = instances[instance_id]
            if instance.get("status") == "RUNNING" and instance.get("ip"):
                ip = instance["ip"]
                keyfile = utils.get_key_file(instance["uuid"])

                if not os.path.exists(keyfile):
                    created, key_error = utils.add_key_to_instance(
                        instance_id, token)
                    if not created or not os.path.exists(keyfile):
                        logger.error(
                            "Failed to create/retrieve SSH key for instance.")
                        return

                try:
                    ssh = robust_ssh_connect(
                        ip, keyfile, max_wait=180, interval=5, username="ubuntu")
                    # Write PID to lockfile only after successful connection
                    # Check if there's already a connection attempt in progress
                    if os.path.exists(lock_file):
                        try:
                            with open(lock_file, 'r') as f:
                                pid = int(f.read().strip())

                            # Check if process exists and it's not our parent
                            if not is_lock_stale(lock_file) and pid != os.getppid():
                                logger.error(
                                    "Another connection attempt is already in progress")
                                return
                            else:
                                # Either stale or our parent process, safe to remove
                                try:
                                    os.remove(lock_file)
                                except Exception as e:
                                    logger.error(
                                        f"Failed to remove stale lockfile: {e}")
                                    return
                        except Exception:
                            # If we can't read the PID, try to remove the lockfile
                            try:
                                os.remove(lock_file)
                            except Exception as e:
                                logger.error(
                                    f"Failed to remove invalid lockfile: {e}")
                                return
                    write_lock_file(lock_file)
                    logger.info(
                        f"Successfully connected to {ip} for instance {instance_id}")

                    # Add token to environment
                    _, stdout, _ = ssh.exec_command(
                        f"sed -i '/export TNR_API_TOKEN/d' /home/ubuntu/.bashrc && echo 'export TNR_API_TOKEN={token}' >> /home/ubuntu/.bashrc")
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status != 0:
                        error = stderr.read().decode().strip()
                        click.echo(click.style(
                            f"Warning: Token environment setup failed: {error}", fg="yellow"))

                    # Update binary and write config
                    has_active_sessions = check_active_ssh_sessions(ssh)
                    if has_active_sessions:
                        pass
                    else:
                        try:
                            # Check for existing config first
                            _, stdout, _ = ssh.exec_command(
                                "cat /home/ubuntu/.thunder/config.json 2>/dev/null || echo ''")
                            existing_config = stdout.read().decode().strip()
                            device_id = None

                            try:
                                if existing_config:
                                    config_data = json.loads(existing_config)
                                    if config_data.get("deviceId") and int(config_data.get("deviceId")) > 0:
                                        device_id = config_data["deviceId"]
                            except Exception:
                                # If we can't parse the existing config, we'll just get a new device ID
                                pass

                            # Only get new device ID if we couldn't read it from existing config
                            if device_id is None:
                                device_id, error = utils.get_next_id(token)
                                if error:
                                    logger.warning(
                                        f"Could not grab next device ID: {error}")
                                    return

                            config = {
                                "instanceId": instance_id,
                                "deviceId": device_id,
                                "gpuType": instance.get('gpuType', 't4').lower(),
                                "gpuCount": int(instance.get('numGpus', 1))
                            }

                            # Update binary and write config in a single command
                            remote_path = '/home/ubuntu/.thunder/libthunder.so'
                            remote_config_path = '/home/ubuntu/.thunder/config.json'
                            remote_token_path = '/home/ubuntu/.thunder/token'
                            thunder_dir = '/etc/thunder'
                            thunder_lib_path = f'{thunder_dir}/libthunder.so'
                            config_json = json.dumps(config, indent=4)

                            commands = [
                                # Create directories with explicit permissions
                                f'sudo install -d -m 755 {thunder_dir}',
                                'sudo install -d -m 755 /home/ubuntu/.thunder',

                                # Back up existing preload file
                                'sudo cp -a /etc/ld.so.preload /etc/ld.so.preload.bak || true',

                                # Download to a temporary file first
                                f'curl -L https://storage.googleapis.com/client-binary/client_linux_x86_64 -o /tmp/libthunder.tmp',
                                f'sudo install -m 755 -o root -g root /tmp/libthunder.tmp {remote_path}',
                                'rm -f /tmp/libthunder.tmp',
                                f'[ -f "{remote_path}" ] && [ -s "{remote_path}" ] || (echo "Download failed" && exit 1)',

                                # Create symlink for libthunder.so
                                f'sudo rm -f {thunder_lib_path} || true',
                                f'sudo ln -sf {remote_path} {thunder_lib_path}',
                                'sudo chown root:root /etc/thunder/libthunder.so',
                                'sudo chmod 755 /etc/thunder/libthunder.so',

                                # Update preload file to use the symlinked path
                                f'echo "{thunder_lib_path}" | sudo tee /etc/ld.so.preload.new',
                                'sudo chown root:root /etc/ld.so.preload.new',
                                'sudo chmod 644 /etc/ld.so.preload.new',
                                'sudo mv /etc/ld.so.preload.new /etc/ld.so.preload',

                                # Write config files
                                f'echo \'{config_json}\' > /tmp/config.tmp',
                                f'sudo install -m 644 -o root -g root /tmp/config.tmp {remote_config_path}',
                                'rm -f /tmp/config.tmp',

                                f'echo \'{token}\' > /tmp/token.tmp',
                                f'sudo install -m 600 -o root -g root /tmp/token.tmp {remote_token_path}',
                                'rm -f /tmp/token.tmp',

                                # Symlink config and token to .thunder
                                'sudo rm -f /etc/thunder/config.json || true',
                                f'sudo ln -sf {remote_config_path} /etc/thunder/config.json',
                                'sudo chown root:root /etc/thunder/config.json',
                                'sudo chmod 644 /etc/thunder/config.json',
                                'sudo rm -f /etc/thunder/token || true',
                                f'sudo ln -sf {remote_token_path} /etc/thunder/token',
                                'sudo chown root:root /etc/thunder/token',
                                'sudo chmod 644 /etc/thunder/token'
                            ]

                            command_string = ' && '.join(commands)
                            _, stdout, stderr = ssh.exec_command(
                                command_string)

                            exit_status = stdout.channel.recv_exit_status()
                            if exit_status != 0:
                                error_message = stderr.read().decode('utf-8')
                                raise Exception(
                                    f"Failed to update binary and write config: {error_message}")

                            output = stdout.read().decode('utf-8')
                            logger.info(
                                f"Binary transfer and config setup completed. Output: {output}")

                        except Exception as e:
                            logger.error(
                                f"Failed to update binary and write config: {e}")
                            return

                    # SSH Config stuff
                    host_alias = f"tnr-{instance_id}"
                    exists, _ = utils.get_ssh_config_entry(host_alias)
                    if not exists:
                        utils.add_instance_to_ssh_config(
                            ip, keyfile, host_alias)
                        logger.info(
                            f"Added new SSH config entry for {instance_id}")
                    else:
                        utils.update_ssh_config_ip(
                            host_alias, ip, keyfile=keyfile)
                        logger.info(f"Updated SSH config IP for {instance_id}")

                    return

                except ssh_exception.AuthenticationException:
                    logger.error(
                        "SSH authentication failed for instance %s", instance_id)
                    return
                except ssh_exception.NoValidConnectionsError:
                    logger.error(
                        "No valid connections could be established to instance %s", instance_id)
                    return
                except ssh_exception.SSHException as e:
                    logger.error(f"SSH error for instance %s: %s",
                                 instance_id, str(e))
                    return
                except Exception as e:
                    logger.error(
                        f"Error connecting to instance {instance_id}: {str(e)}")
                    return

            attempt += 1
            time.sleep(2)

        logger.error(f"Timed out waiting for instance {instance_id} to start")
    finally:
        # Always remove the lockfile, even if we error out
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception as e:
            logger.error(f"Failed to remove lockfile: {e}")


def start_background_config(instance_id, token):
    """
    Spawn the background process to handle SSH configuration
    """
    # Instead of trying to re-run the script, we'll run Python with the command directly
    cmd = [
        sys.executable,
        "-c",
        f"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath('{os.path.dirname(__file__)}'))))
from thunder import utils
from thunder.thunder import wait_and_configure_ssh
wait_and_configure_ssh('{instance_id}', '{token}')
        """
    ]

    try:
        Popen(
            cmd,
            start_new_session=True,  # Detach from parent process
            stdout=open(os.devnull, 'w'),
            stderr=open(os.devnull, 'w')
        )
    except Exception as e:
        # Log error but don't fail the main command
        logger = logging.getLogger("thunder")
        logger.error(f"Failed to start background configuration: {e}")


@cli.command(
    help="Start a stopped Thunder Compute instance. All data in the persistent storage will be preserved",
    hidden=INSIDE_INSTANCE,
)
@click.argument("instance_id", required=True)
def start(instance_id):
    with DelayedProgress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("Loading", total=None)
        token = get_token()

        # First check instance status
        success, error, instances = utils.get_instances(token, use_cache=False)
        if not success:
            if "Unauthorized" in error:
                raise click.ClickException(
                    UNAUTHORIZED_ERROR
                )
            else:
                raise click.ClickException(
                    f"Failed to get instance status: {error}"
                )

        instance = instances.get(instance_id)
        if not instance:
            raise click.ClickException(f"Instance {instance_id} not found")

        if instance["status"] == "STOPPING":
            raise click.ClickException(
                f"Cannot start instance {instance_id} while it is stopping. Please wait for it to fully stop first.")

        if instance["status"] == "RUNNING":
            click.echo(click.style(
                f"Instance {instance_id} is already running", fg="yellow"))
            return

        success, error = utils.start_instance(instance_id, token)

    if success:
        # Attempt immediate key creation
        if not utils.add_key_to_instance(instance_id, token):
            click.echo(click.style(
                f"Warning: Unable to create or attach SSH key for instance {instance_id} at start. The background config will retry automatically.",
                fg="yellow"
            ))

        start_background_config(instance_id, token)
        click.echo(
            click.style(
                f"Successfully started Thunder Compute instance {instance_id}",
                fg="cyan",
            )
        )
    else:
        raise click.ClickException(
            f"Failed to start Thunder Compute instance {instance_id}: {error}"
        )


@cli.command(hidden=True)
@click.argument("instance_id")
@click.argument("token")
def background_config(instance_id, token):
    """Hidden command to handle background SSH configuration"""
    wait_and_configure_ssh(instance_id, token)


@cli.command(
    help="Stop a running Thunder Compute instance. Stopped instances have persistent storage and can be restarted at any time",
    hidden=INSIDE_INSTANCE,
)
@click.argument("instance_id", required=True)
def stop(instance_id):
    with DelayedProgress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("Loading", total=None)  # No description text
        token = get_token()
        _, _, instances = utils.get_instances(token, use_cache=False)
        for instance in instances:
            instance_not_found = True
            if instance == instance_id:
                instance_not_found = False
                success, error = utils.stop_instance(instance_id, token)
                break
    if instance_not_found:
        raise click.ClickException(f"Instance {instance_id} not found")
    elif success:
        click.echo(
            click.style(
                f"Successfully stopped Thunder Compute instance {instance_id}",
                fg="cyan",
            )
        )
        try:
            device_ip = instances[instance_id]['ip']
            utils.remove_host_key(device_ip)
            utils.remove_instance_from_ssh_config(f"tnr-{instance_id}")
        except Exception as _:
            pass
    else:
        raise click.ClickException(
            f"Failed to stop Thunder Compute instance {instance_id}: {error}"
        )


def get_next_drive_letter():
    """Find the next available drive letter on Windows"""
    if platform.system() != "Windows":
        return None

    used_drives = set()
    for letter in ascii_uppercase:
        if os.path.exists(f"{letter}:"):
            used_drives.add(letter)

    for letter in ascii_uppercase:
        if letter not in used_drives:
            return f"{letter}:"
    raise RuntimeError("No available drive letters")


def cleanup_mount(mount_point, hide_warnings=False):
    """Unmount the SMB share"""
    os_type = platform.system()

    if os_type == "Windows":
        if ":" in str(mount_point):  # It's a drive letter
            cmd = ["net", "use", str(mount_point), "/delete", "/y"]
    elif os_type == "Darwin":
        cmd = ["diskutil", "unmount", str(mount_point)]
    else:  # Linux
        cmd = ["sudo", "umount", str(mount_point)]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        click.echo(click.style(f"📤 Unmounted {mount_point}", fg="yellow"))
    except subprocess.CalledProcessError:
        if not hide_warnings:
            click.echo(click.style(
                f"⚠️  Failed to unmount {mount_point}", fg="red"))


def mount_smb_share(share_name):
    """
    Mount SMB share based on OS and share_name under ~/tnrmount/<share_name> on non-Windows.
    On Windows, assign a drive letter.
    """
    os_type = platform.system()
    base_mount_dir = os.path.expanduser(base_mount_dir)
    if os_type != "Windows":
        local_mount_point = base_mount_dir / share_name
        local_mount_point = local_mount_point.expanduser()
    else:
        local_mount_point = get_next_drive_letter()

    # Attempt to unmount if exists
    if os_type != "Windows" and local_mount_point.exists():
        cleanup_mount(local_mount_point, hide_warnings=True)

    try:
        if os_type == "Windows":
            # Ensure the SMB share is accessible on default SMB port 445
            # Requires `ssh -L 445:localhost:445 ubuntu@<instance_ip>` done beforehand.

            # Use a standard UNC path without port
            net_cmd = "C:\\Windows\\System32\\net.exe"
            if not os.path.exists(net_cmd):
                net_cmd = "net"  # fallback if System32 isn't accessible

            cmd = [net_cmd, "use", local_mount_point,
                   f"\\\\localhost\\{share_name}", '/TCPPORT:1445']
            subprocess.run(cmd, check=True, capture_output=True)
            return local_mount_point
        else:
            local_mount_point.mkdir(parents=True, exist_ok=True)
            if os_type == "Linux":
                click.echo(click.style(
                    f"Mounting SMB share {share_name} to {local_mount_point}. You may be required to enter your password.", fg="cyan"))
                cmd = [
                    "sudo", "mount", "-t", "cifs", f"//localhost/{share_name}", str(
                        local_mount_point),
                    "-o", "user=guest,password='',port=1445,rw"
                ]
            else:  # macOS
                cmd = [
                    "mount_smbfs", f"//guest@localhost:1445/{share_name}", str(local_mount_point)]

            subprocess.run(cmd, check=True,
                           stderr=subprocess.DEVNULL, timeout=5)
            return local_mount_point
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode(
            'utf-8', errors='ignore') if e.stderr else str(e)
        if 'exit status 32' in error_msg and os_type == "Linux":
            click.echo(click.style(
                f"❌ To enable SMB mounting, cifs-utils must be installed. If you'd like to connect to the instance without mounting, please use the --nomount flag", fg="red"))
        else:
            click.echo(click.style(
                f"❌ Error mounting share '{share_name}'", fg="red"))
            if IS_WINDOWS:
                click.echo(click.style(
                    f"If you're seeing issues mounting network shares, you may want to turning off the Windows SMB server and restarting.", fg="cyan"))
        raise
    except subprocess.TimeoutExpired:
        click.echo(click.style(
            f"❌ Error mounting share '{share_name}'", fg="red"))
        if os_type == "Darwin":
            click.echo("""
Looks like you're on a Mac. Try restarting the SMB process:
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.smbd.plist
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.smbd.plist
sudo defaults write /Library/Preferences/SystemConfiguration/com.apple.smb.server.plist EnabledServices -array disk
            """, fg="cyan")
        raise


def configure_remote_samba_shares(ssh, shares):
    """
    Append shares configuration to remote /etc/samba/shares.conf (included by smb.conf) and restart smbd.
    Backup original config first.
    """
    # Ensure shares.conf exists
    stdin, stdout, stderr = ssh.exec_command(
        "sudo touch /etc/samba/shares.conf && sudo chmod 644 /etc/samba/shares.conf")
    stdout.read()
    err = stderr.read().decode()
    if err:
        raise RuntimeError(f"Error preparing shares.conf: {err}")

    backup_cmd = "sudo cp /etc/samba/shares.conf /etc/samba/shares.conf.bak"
    stdin, stdout, stderr = ssh.exec_command(backup_cmd)
    stdout.read()
    err = stderr.read().decode()
    if err:
        # Not critical if backup fails (maybe first time run), but let's warn
        click.echo(click.style(
            f"⚠️ Warning: Could not backup shares.conf: {err}", fg="yellow"))

    # Build share config
    share_config_lines = []
    for share in shares:
        share_config_lines.append(f"[{share['name']}]")
        share_config_lines.append(f"path = {share['path']}")
        share_config_lines.append("browseable = yes")
        share_config_lines.append("writable = yes")
        share_config_lines.append("read only = no")
        share_config_lines.append("guest ok = yes")
        share_config_lines.append("force user = root")
        share_config_lines.append("create mask = 0777")
        share_config_lines.append("directory mask = 0777")
        share_config_lines.append("")
    share_config = "\n".join(share_config_lines)

    # Write shares to shares.conf (overwrite rather than append to keep control)
    cmd = f'echo "{share_config}" | sudo tee /etc/samba/shares.conf'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()
    err = stderr.read().decode()
    if err:
        raise RuntimeError(f"Error writing shares to shares.conf: {err}")

    # Restart Samba service
    restart_cmd = "sudo systemctl restart smbd"
    stdin, stdout, stderr = ssh.exec_command(restart_cmd)
    stdout.read()
    err = stderr.read().decode()
    if err:
        raise RuntimeError(f"Error restarting smbd: {err}")


def restore_original_smb_conf(ssh):
    """
    Restore the original shares.conf and restart Samba.
    """
    restore_cmd = "sudo cp /etc/samba/shares.conf.bak /etc/samba/shares.conf && sudo systemctl restart smbd"
    _, stdout, stderr = ssh.exec_command(restore_cmd)
    stdout.read()
    err = stderr.read().decode()
    if err:
        # If restore failed, just warn
        click.echo(click.style(
            f"⚠️  Failed to restore original shares.conf: {err}", fg="red"))


def echo_openssh_instructions():
    """Echo the OpenSSH instructions in a nicely formatted panel."""
    instructions = [
        "[white]1. Open Windows Settings (Windows key + I)",
        "2. Go to System > Optional features",
        "3. Click '+ Add a feature'",
        "4. Search for 'OpenSSH Client'",
        "5. Click Install",
        "6. Restart your terminal[/white]"
    ]

    panel = Panel(
        "\n".join(instructions),
        title="[cyan]Install OpenSSH Client[/cyan]",
        title_align="left",
        border_style="cyan",
        highlight=True,
        width=60,
        box=box.ROUNDED
    )
    Console().print(panel)


def check_windows_openssh():
    """Check if OpenSSH is available on Windows and provide guidance if it's not."""
    if not IS_WINDOWS:
        return True

    try:
        # Try to run ssh to check if it exists
        subprocess.run(["ssh", "-V"], capture_output=True, check=True)
        return True
    except FileNotFoundError:
        # Check if we're running in PowerShell
        try:
            # This command will succeed in PowerShell and fail in cmd/other shells
            subprocess.run(
                ["powershell", "-Command", "$PSVersionTable"], capture_output=True, check=True)
            is_powershell = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            is_powershell = False

        if is_powershell:
            click.echo(click.style(
                "\n🔍 OpenSSH is not installed. Attempting to install automatically. This may take a few minutes...", fg="yellow"))
            try:
                # Get the latest OpenSSH version and install it
                install_command = """
                $ErrorActionPreference = 'Stop'
                try {
                    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
                    Write-Output "ISADMIN:$isAdmin"
                    $sshCapability = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Client*' | Select-Object -First 1
                    if ($sshCapability) {
                        Add-WindowsCapability -Online -Name $sshCapability.Name
                        Write-Output $sshCapability.Name
                    } else {
                        Write-Error "OpenSSH Client package not found"
                    }
                } catch {
                    Write-Error $_.Exception.Message
                    exit 1
                }
                """
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive",
                        "-Command", install_command],
                    capture_output=True,
                    text=True
                )

                # Check if we're admin from PowerShell output
                is_admin = "ISADMIN:True" in result.stdout

                if result.returncode == 0 and "OpenSSH.Client" in result.stdout:
                    version = [line for line in result.stdout.splitlines(
                    ) if "OpenSSH.Client" in line][0]
                    click.echo(click.style(
                        f"✅ Successfully installed OpenSSH {version}!", fg="green"))
                    click.echo(click.style(
                        "🔄 Please restart your terminal for the changes to take effect.", fg="cyan"))
                    return False
                else:
                    error_output = result.stderr.strip() if result.stderr else "Unknown error"
                    if "requires elevation" in error_output.lower() or "administrator" in error_output.lower():
                        click.echo(click.style(
                            "\n❌ Administrator privileges required for installation.", fg="red"))
                        click.echo(click.style(
                            "Please run your terminal as Administrator and try again. Alternatively:", fg="yellow"))
                        echo_openssh_instructions()
                    else:
                        click.echo(click.style(
                            f"\n❌ Failed to install OpenSSH: {error_output}", fg="red"))
                        if is_admin:
                            click.echo(click.style(
                                "\nSince automatic installation failed with admin privileges, try these manual steps:", fg="cyan"))
                            echo_openssh_instructions()
            except Exception as e:
                # Handle any other exceptions that might occur
                error_msg = str(e)
                click.echo(click.style(
                    "\n❌ Automatic installation failed.", fg="red"))
                click.echo(click.style(f"Error: {error_msg}", fg="yellow"))

        # If not in PowerShell or auto-install failed without admin, show standard instructions
        if not is_powershell:
            echo_openssh_instructions()
            click.echo(click.style(
                "\nAlternatively, you can run PowerShell as Administrator and run 'tnr connect' again", fg="cyan"))
        return False
    except subprocess.CalledProcessError:
        return False


@cli.command(
    help="Connect to the Thunder Compute instance with the specified instance_id",
)
@click.argument("instance_id", required=False)
@click.option("-t", "--tunnel", type=int, multiple=True, help="Forward specific ports from the remote instance to your local machine (e.g. -t 8080 -t 3000). Can be specified multiple times")
@click.option("--mount", type=str, multiple=True, help="Mount local folders to the remote instance. Specify the remote path (e.g. --mount /home/ubuntu/data). Can use ~ for home directory. Can be specified multiple times")
@click.option("--nomount", is_flag=True, default=False, help="Disable automatic folder mounting, including template-specific defaults like ComfyUI folders")
@click.option("--debug", is_flag=True, default=False, hidden=True, help="Show debug timing information")
@coro # Asynchronous decorator
async def connect(tunnel, instance_id=None, mount=None, nomount=False, debug=False):
    # Start fetching the latest hash immediately
    latest_hash_task = asyncio.create_task(utils.get_latest_client_binary_hash_async())

    # Check for OpenSSH on Windows first
    if not check_windows_openssh():
        return

    # Initialize timing dictionary to store all timings
    timings = {}
    start_time = time.time()

    instance_id = instance_id or "0"
    click.echo(click.style(
        f"Connecting to Thunder Compute instance {instance_id}...", fg="cyan"))

    # Check for existing lockfile
    lock_check_start = time.time()
    lock_file = get_instance_lock_file(instance_id)
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if it's our own process (parent process)
            if pid == os.getppid():
                # This is a background config we spawned, wait for it
                click.echo(click.style(
                    "Waiting for background configuration to complete...", fg="yellow"))
                if not wait_for_background_config(instance_id):
                    raise click.ClickException(
                        "Timed out waiting for background configuration to complete. Please try again or contact support@thundercompute.com"
                    )
            elif is_lock_stale(lock_file):
                try:
                    os.remove(lock_file)
                except Exception:
                    pass
        except ValueError:
            try:
                os.remove(lock_file)
            except Exception:
                pass
    timings['lock_check'] = time.time() - lock_check_start

    # Create our own lockfile
    try:
        write_lock_start = time.time()
        write_lock_file(lock_file)
        timings['write_lock'] = time.time() - write_lock_start

        token_start = time.time()
        token = get_token()
        timings['get_token'] = time.time() - token_start

        instances_start = time.time()
        success, error, instances = utils.get_instances(token, update_ips=True)
        if not success:
            if "Unauthorized" in error:
                raise click.ClickException(
                    UNAUTHORIZED_ERROR
                )
            else:
                raise click.ClickException(
                    f"Failed to list Thunder Compute instances: {error}")
        timings['get_instances'] = time.time() - instances_start

        instance_check_start = time.time()
        instance = next(((curr_id, meta) for curr_id,
                        meta in instances.items() if curr_id == instance_id), None)
        if not instance:
            raise click.ClickException(
                f"Unable to find instance {instance_id}. Check available instances with `tnr status`"
            )

        instance_id, metadata = instance
        ip = metadata.get("ip")
        status = metadata.get("status")
        if status.upper() != "RUNNING":
            raise click.ClickException(
                f"Unable to connect to instance {instance_id}, the instance is not running. (status: {status})."
            )
        if not ip:
            raise click.ClickException(
                f"Unable to connect to instance {instance_id}, the instance is not reporting an IP address (is it fully started?)."
            )
        timings['instance_check'] = time.time() - instance_check_start

        keyfile_start = time.time()
        keyfile = utils.get_key_file(metadata["uuid"])
        if not os.path.exists(keyfile):
            created, key_error = utils.add_key_to_instance(instance_id, token)
            if not created or not os.path.exists(keyfile):
                # improved error usage
                user_msg = key_error or f"Unable to find or create a valid SSH key for instance {instance_id}."
                raise click.ClickException(user_msg)
        timings['keyfile_setup'] = time.time() - keyfile_start

        # Attempt SSH connection
        ssh_connect_start = time.time()
        try:
            ssh = robust_ssh_connect(
                ip, keyfile, max_wait=120, interval=1, username="ubuntu")
        except click.ClickException as e:
            # Pass through Click exceptions directly
            raise
        except Exception as e:
            raise click.ClickException(
                f"Failed to connect to instance {instance_id}: {str(e)}")
        timings['ssh_connect'] = time.time() - ssh_connect_start

        # Add token to environment
        token_env_start = time.time()
        _, stdout, stderr = ssh.exec_command(
            f"sed -i '/export TNR_API_TOKEN/d' /home/ubuntu/.bashrc && echo 'export TNR_API_TOKEN={token}' >> /home/ubuntu/.bashrc")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error = stderr.read().decode().strip()
            click.echo(click.style(
                f"Warning: Token environment setup failed: {error}", fg="yellow"))
        timings['token_env_setup'] = time.time() - token_env_start

        # Check for active SSH sessions before updating binary and writing config
        binary_update_start = time.time()
        has_active_sessions = check_active_ssh_sessions(ssh)
        if not has_active_sessions:
            # Check for existing config first
            _, stdout, _ = ssh.exec_command(
                "cat /home/ubuntu/.thunder/config.json 2>/dev/null || echo ''")
            existing_config = stdout.read().decode().strip()
            device_id = None
            gpu_type = None
            gpu_count = None
            try:
                if existing_config:
                    config_data = json.loads(existing_config)
                    if config_data.get("deviceId") and int(config_data.get("deviceId")) > 0:
                        device_id = config_data["deviceId"]
                        gpu_type = config_data["gpuType"]
                        gpu_count = config_data["gpuCount"]

            except Exception:
                # If we can't parse the existing config, we'll just get a new device ID
                pass

            update_binary = True
            # Only get new device ID if we couldn't read it from existing config
            if device_id is None:
                device_id, error = utils.get_next_id(token)
                if error:
                    raise click.ClickException(
                        f"Could not grab next device ID: {error}")

            if gpu_type is not None and gpu_count is not None:
                if gpu_type == metadata.get('gpuType', 't4').lower() and int(gpu_count) == int(metadata.get('numGpus', 1)):

                    # Get existing binary hash
                    _, stdout, _ = ssh.exec_command(
                        "md5sum /home/ubuntu/.thunder/libthunder.so 2>/dev/null || echo ''")
                    existing_binary_hash = stdout.read(
                    ).decode().strip().split(" ")[0]

                    # Now get the result from the async task started earlier
                    latest_binary_hash = await latest_hash_task

                    # Compare the hashes
                    if latest_binary_hash is not None and existing_binary_hash == latest_binary_hash:
                        update_binary = False
                    else:
                        # If hashes don't match, or we couldn't get the latest hash, update
                        update_binary = True
                else:
                    # If we didn't have prior gpu_type/gpu_count, force update check
                    update_binary = True

            if update_binary:

                config = {
                    "instanceId": instance_id,
                    "deviceId": device_id,
                    "gpuType": metadata.get('gpuType', 't4').lower(),
                    "gpuCount": int(metadata.get('numGpus', 1))
                }

                # Update binary and write config in a single command
                try:
                    remote_path = '/home/ubuntu/.thunder/libthunder.so'
                    remote_config_path = '/home/ubuntu/.thunder/config.json'
                    remote_token_path = '/home/ubuntu/.thunder/token'
                    thunder_dir = '/etc/thunder'
                    thunder_lib_path = f'{thunder_dir}/libthunder.so'
                    config_json = json.dumps(config, indent=4)

                    commands = [
                        # Create directories with explicit permissions
                        f'sudo install -d -m 755 {thunder_dir}',
                        'sudo install -d -m 755 /home/ubuntu/.thunder',

                        # Back up existing preload file
                        'sudo cp -a /etc/ld.so.preload /etc/ld.so.preload.bak || true',

                        # Download to a temporary file first
                        f'curl -L https://storage.googleapis.com/client-binary/client_linux_x86_64 -o /tmp/libthunder.tmp',
                        f'sudo install -m 755 -o root -g root /tmp/libthunder.tmp {remote_path}',
                        'rm -f /tmp/libthunder.tmp',
                        f'[ -f "{remote_path}" ] && [ -s "{remote_path}" ] || (echo "Download failed" && exit 1)',

                        # Create symlink for libthunder.so
                        f'sudo rm -f {thunder_lib_path} || true',
                        f'sudo ln -sf {remote_path} {thunder_lib_path}',
                        'sudo chown root:root /etc/thunder/libthunder.so',
                        'sudo chmod 755 /etc/thunder/libthunder.so',

                        # Update preload file to use the symlinked path
                        f'echo "{thunder_lib_path}" | sudo tee /etc/ld.so.preload.new',
                        'sudo chown root:root /etc/ld.so.preload.new',
                        'sudo chmod 644 /etc/ld.so.preload.new',
                        'sudo mv /etc/ld.so.preload.new /etc/ld.so.preload',

                        # Write config files
                        f'echo \'{config_json}\' > /tmp/config.tmp',
                        f'sudo install -m 644 -o root -g root /tmp/config.tmp {remote_config_path}',
                        'rm -f /tmp/config.tmp',

                        f'echo \'{token}\' > /tmp/token.tmp',
                        f'sudo install -m 600 -o root -g root /tmp/token.tmp {remote_token_path}',
                        'rm -f /tmp/token.tmp',

                        # Symlink config and token to .thunder
                        'sudo rm -f /etc/thunder/config.json || true',
                        f'sudo ln -sf {remote_config_path} /etc/thunder/config.json',
                        'sudo chown root:root /etc/thunder/config.json',
                        'sudo chmod 644 /etc/thunder/config.json',
                        'sudo rm -f /etc/thunder/token || true',
                        f'sudo ln -sf {remote_token_path} /etc/thunder/token',
                        'sudo chown root:root /etc/thunder/token',
                        'sudo chmod 644 /etc/thunder/token'
                    ]

                    command_string = ' && '.join(commands)
                    _, stdout, stderr = ssh.exec_command(command_string)

                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status != 0:
                        error_message = stderr.read().decode('utf-8')
                        raise click.ClickException(
                            f"Failed to update binary and write config: {error_message}")
                except Exception as e:
                    raise click.ClickException(
                        f"Failed to update binary and write config: {e}")
        timings['binary_update'] = time.time() - binary_update_start

        # Add to SSH config
        try:
            ssh_config_start = time.time()
            host_alias = f"tnr-{instance_id}"
            exists, _ = utils.get_ssh_config_entry(host_alias)
            if not exists:
                utils.add_instance_to_ssh_config(ip, keyfile, host_alias)
            else:
                utils.update_ssh_config_ip(host_alias, ip, keyfile=keyfile)
            timings['ssh_config_setup'] = time.time() - ssh_config_start
        except Exception as e:
            click.echo(click.style(
                f"Error adding instance to SSH config. Proceeding with connection... {e}", fg="red"))

        tunnel_setup_start = time.time()
        tunnel_args = []
        for port in tunnel:
            tunnel_args.extend(["-L", f"{port}:localhost:{port}"])

        template = metadata.get('template', 'base')
        template_ports = OPEN_PORTS.get(template, [])
        for port in template_ports:
            tunnel_args.extend(["-L", f"{port}:localhost:{port}"])
        timings['tunnel_setup'] = time.time() - tunnel_setup_start

        mount = list(mount)

        # Automatically mount folders for templates - don't do this for Windows
        mount_setup_start = time.time()
        if template in AUTOMOUNT_FOLDERS.keys() and not nomount and not IS_WINDOWS:
            if AUTOMOUNT_FOLDERS[template] not in mount and AUTOMOUNT_FOLDERS[template] is not None:
                mount.append(AUTOMOUNT_FOLDERS[template])

        shares_to_mount = []
        remote_home = "/home/ubuntu"
        for share_path in mount:
            # Expand ~ to /home/ubuntu if present
            # This is still allowed, just optional
            remote_home = "/home/ubuntu"
            if share_path.startswith("~"):
                share_path = share_path.replace("~", remote_home, 1)

            if share_path.startswith(remote_home):
                chmod_cmd = f"sudo chmod -R 777 '{share_path}'"
                ssh.exec_command(chmod_cmd)
            # Just ensure directory exists
            _, stdout, _ = ssh.exec_command(
                f"[ -d '{share_path}' ] && echo 'OK' || echo 'NO'")
            result = stdout.read().decode().strip()
            if result != "OK":
                raise click.ClickException(
                    f"The directory '{share_path}' does not exist on the remote instance.")

            share_name = os.path.basename(share_path.strip("/")) or "root"

            shares_to_mount.append({
                "name": share_name,
                "path": share_path
            })
        timings['mount_setup'] = time.time() - mount_setup_start

        ssh_interactive_cmd = [
            "ssh",
            "-q",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "IdentitiesOnly=yes",
            "-o", "UserKnownHostsFile=/dev/null",
            # Add SSH multiplexing options
            "-i", keyfile,
            "-t"
        ] + tunnel_args + [
            f"ubuntu@{ip}"
        ]

        if not IS_WINDOWS:
            ssh_interactive_cmd.extend([
                "-o", "ControlMaster=auto",
                "-o", "ControlPath=~/.thunder/thunder-control-%h-%p-%r",  # Use %r for remote username
                "-o", "ControlPersist=5m",  # Keep control connection open for 5 minutes
            ])

        smb_tunnel_cmd = [
            "ssh",
            "-q",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "IdentitiesOnly=yes",
            "-i", keyfile,
            "-L", "1445:localhost:445",
            "-N",
            f"ubuntu@{ip}"
        ]

        tunnel_process = None
        mounted_points = []

        def cleanup():
            for mp in mounted_points:
                cleanup_mount(mp)
            if tunnel_process and tunnel_process.poll() is None:
                tunnel_process.terminate()
                tunnel_process.wait()
            restore_original_smb_conf(ssh)

        try:
            smb_setup_start = time.time()
            if shares_to_mount and not nomount:
                atexit.register(cleanup)
                # Configure shares on remote
                try:
                    configure_remote_samba_shares(ssh, shares_to_mount)
                except Exception as e:
                    click.echo(click.style(
                        f"❌ Error configuring samba shares: {e}", fg="red"))
                    return

                # Start SMB tunnel
                tunnel_process = subprocess.Popen(
                    smb_tunnel_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Test tunnel
                max_retries = 3
                for attempt in range(max_retries):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    try:
                        s.connect(("localhost", 1445))
                        s.close()
                        break
                    except socket.error:
                        s.close()
                        if attempt < max_retries - 1:
                            click.echo(click.style(
                                "Retrying SMB tunnel connection...", fg="yellow"))
                            time.sleep(2)
                        else:
                            raise RuntimeError(
                                "Failed to establish SMB tunnel")

                # Mount each share
                for share in shares_to_mount:
                    share_name = share["name"]
                    click.echo(click.style(
                        f"📥 Mounting SMB share '{share_name}'...", fg="green"))
                    try:
                        mp = mount_smb_share(share_name)
                        mounted_points.append(mp)
                        click.echo(click.style(
                            f"✅ Mounted {share_name} at {mp}\n", fg="green"))
                    except Exception:
                        # If mounting fails for this share, cleanup will occur at exit
                        pass
            timings['smb_setup'] = time.time() - smb_setup_start

            # Delete lockfile if it exists
            if os.path.exists(lock_file):
                os.remove(lock_file)

            # Print timing summary before interactive session
            if debug:
                total_time = time.time() - start_time
                click.echo("\n🕒 Connection timing breakdown:")
                for operation, duration in timings.items():
                    percentage = (duration / total_time) * 100
                    click.echo(
                        f"  • {operation}: {duration:.2f}s ({percentage:.1f}%)")
                click.echo(f"  Total setup time: {total_time:.2f}s\n")

            # Start interactive SSH
            subprocess.run(ssh_interactive_cmd)
        except KeyboardInterrupt:
            click.echo(click.style("\n🛑 Interrupted by user", fg="yellow"))
        except Exception as e:
            click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        finally:
            click.echo(click.style("⚡ Exiting thunder instance ⚡", fg="green"))
    finally:
        # Always clean up our lockfile
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception as e:
            pass


def _complete_path(ctx, param, incomplete):
    """Custom path completion that handles both local paths and remote paths."""
    # Unix-style path handling for remote paths
    if ':' in incomplete:
        instance_id, path = incomplete.split(':', 1)
        return []

    # For local paths, use Click's built-in path completion
    return click.Path(exists=True).shell_complete(ctx, param, incomplete)


def _parse_path(path):
    """Parse a path into (instance_id, path) tuple."""
    # First check if it matches the remote path pattern (instance_id:path)
    parts = path.split(":", 1)
    if len(parts) > 1:
        # Check if this is actually a Windows drive path (e.g. C:\path)
        if platform.system() == "Windows" and len(parts[0]) == 1 and parts[0].isalpha():
            return (None, path)
        # Handle Windows UNC paths (e.g. \\server\share)
        if platform.system() == "Windows" and path.startswith("\\\\"):
            return (None, path)
        return (parts[0], parts[1])

    return (None, path)


@cli.command()
@click.argument("source_paths", nargs=-1, required=True, shell_complete=_complete_path if not platform.system() == "Windows" else None)
@click.argument("destination_path", required=True, shell_complete=_complete_path if not platform.system() == "Windows" else None)
def scp(source_paths, destination_path):
    """Transfers files between your local machine and Thunder Compute instances.

    Arguments:\n
        SOURCE_PATHS: One or more paths to copy from. For instance files use 'instance_id:/path/to/file'\n
        DESTINATION_PATH: Path to copy to. For instance files use 'instance_id:/path/to/file'\n\n

    Examples:\n
        Copy local file or folder to instance\n
            $ tnr scp myfile.py 0:/home/ubuntu/\n
        Copy from instance to local\n
            $ tnr scp 0:/home/ubuntu/results.csv ./\n
        Copy multiple files using glob pattern (only supported local -> remote)\n
            $ tnr scp thunder/*.txt 0:/home/ubuntu/\n
        Copy multiple specific files\n
            $ tnr scp file1.py file2.py 0:/home/ubuntu/
    """
    try:
        token = get_token()
        success, error, instances = utils.get_instances(token)
        if not success:
            if "Unauthorized" in error:
                raise click.ClickException(
                    UNAUTHORIZED_ERROR
                )
            else:
                raise click.ClickException(
                    f"Failed to list Thunder Compute instances: {error}")

        # Parse destination path
        dst_instance, dst_path = _parse_path(destination_path)

        # Parse and validate all source paths
        src_instances = set()
        local_paths = []
        remote_paths = []

        for path in source_paths:
            instance_id, path_part = _parse_path(path)
            if instance_id:
                src_instances.add(instance_id)
                remote_paths.append(path_part)
            else:
                local_paths.append(path)

        # Validate that exactly one instance is involved
        all_instances = set(src_instances)
        if dst_instance:
            all_instances.add(dst_instance)
        if len(all_instances) > 1:
            raise click.ClickException(
                "Cannot transfer files between different instances. Please transfer through your local machine first.")

        # Determine direction and get instance details
        instance_id = next(iter(all_instances))
        local_to_remote = bool(dst_instance)

        if instance_id not in instances:
            raise click.ClickException(f"Instance '{instance_id}' not found")

        metadata = instances[instance_id]
        if not metadata["ip"]:
            raise click.ClickException(
                f"Instance {instance_id} is not available. Use 'tnr status' to check if the instance is running"
            )

        # Setup SSH connection
        ssh = _setup_ssh_connection(instance_id, metadata, token)

        # If we have multiple files, ensure destination is a directory
        source_count = len(local_paths) + len(remote_paths)
        if source_count > 1:
            if not dst_path.endswith('/') and not dst_path.endswith('\\'):
                raise click.ClickException(
                    "When copying multiple files, destination must be a directory (end with / or \\)")

            # Verify remote directory exists if destination is remote
            if dst_instance and not _verify_remote_path(ssh, dst_path):
                raise click.ClickException(
                    f"Remote directory '{dst_path}' does not exist on instance {instance_id}"
                )

        # Calculate total size for progress bar
        total_size = 0
        try:
            for source_path in source_paths:
                size = None
                if local_to_remote:
                    size = _get_local_size(source_path)
                else:
                    src_instance, src_path = _parse_path(source_path)
                    size = _get_remote_size(ssh, src_path)
                if size is not None:  # Only add if we got a valid size
                    total_size += size
        except Exception as e:
            click.echo(click.style(
                "Warning: Could not pre-calculate total size", fg="yellow"))
            total_size = None

        # Setup progress bar
        with Progress(
            BarColumn(
                complete_style="cyan",
                finished_style="cyan",
                pulse_style="white"
            ),
            TextColumn("[cyan]{task.description}", justify="right"),
            transient=False  # Changed from True to False to keep progress bar visible
        ) as progress:
            task = progress.add_task(
                description="Starting transfer...",
                total=total_size
            )

            # Only show the "Copying files" message if we have multiple files
            if source_count > 1:
                click.echo(click.style(
                    f"Copying {source_count} files to {dst_path} on remote instance {instance_id}...",
                    fg="white"
                ))

            total_files = 0
            total_transferred = 0

            # Perform transfer for each file
            for source_path in source_paths:
                # Parse the source path again for each file
                src_instance, src_path = _parse_path(source_path)

                # Prepare paths for this transfer
                local_path = source_path if local_to_remote else destination_path
                remote_path = dst_path if local_to_remote else src_path
                remote_path = remote_path or "~/"

                # Normalize paths for Windows
                if platform.system() == "Windows":
                    # Store original path for error messages
                    original_local_path = local_path

                    # Convert to proper Windows path
                    local_path = os.path.normpath(local_path)

                    # Handle relative paths starting with ./ or .\ by removing them
                    if local_path.startswith('.\\') or local_path.startswith('./'):
                        local_path = local_path[2:]

                    # Handle current directory
                    if local_path == '.':
                        local_path = os.getcwd()

                    # For display purposes
                    display_path = original_local_path
                else:
                    display_path = local_path

                # Verify remote path exists before transfer
                if not local_to_remote:
                    if not _verify_remote_path(ssh, remote_path):
                        raise click.ClickException(
                            f"Remote path '{remote_path}' does not exist on instance {instance_id}"
                        )

                # Perform transfer
                files, transferred = _perform_transfer(
                    ssh,
                    local_path,
                    remote_path,
                    instance_id,
                    local_to_remote,
                    progress,
                    task
                )
                total_files += files
                total_transferred += transferred

            # Only show success message if we actually transferred files
            if total_files > 0:
                # Update progress bar to show completion
                progress.update(task, completed=total_size)
                progress.update(
                    task, description=f"Successfully transferred {total_files} file{'s' if total_files != 1 else ''} ({_format_size(total_transferred)})")
                # Add a small delay to show the completion state
                time.sleep(0.5)

    except paramiko.SSHException as e:
        raise click.ClickException(f"SSH connection error: {str(e)}")
    except SCPException as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg:
            if local_to_remote:
                raise click.ClickException(
                    f"Local file '{display_path}' not found")
            else:
                raise click.ClickException(
                    f"Remote file '{remote_path}' not found on instance {instance_id}"
                )
        raise click.ClickException(f"SCP transfer failed: {error_msg}")
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


def _format_size(size):
    """Format size in bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def _verify_remote_path(ssh, path):
    """Check if remote path exists. If allow_glob is True, expands glob patterns."""
    # Escape the path for shell
    escaped_path = path.replace('"', '\\"')

    # Standard path verification with proper escaping
    cmd = f'test -e "$(eval echo "{escaped_path}")" && echo "EXISTS"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode().strip() == "EXISTS"


def _setup_ssh_connection(instance_id, metadata, token):
    """Setup and return SSH connection to instance."""
    keyfile = utils.get_key_file(metadata["uuid"])
    if not os.path.exists(keyfile):
        if not utils.add_key_to_instance(instance_id, token):
            raise click.ClickException(
                f"Unable to find or create SSH key file for instance {instance_id}"
            )

    # Try to connect for up to 60 seconds
    start_time = time.time()
    last_error = None
    while time.time() - start_time < 60:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                metadata["ip"],
                username="ubuntu",
                key_filename=keyfile,
                allow_agent=False,
                look_for_keys=False,
                timeout=10
            )
            return ssh
        except Exception as e:
            last_error = e
            time.sleep(2)  # Add small delay between retries

    raise click.ClickException(
        f"Failed to connect to instance {instance_id} after 60 seconds: {str(last_error)}"
    )


def _get_remote_size(ssh, path):
    """Calculate total size of remote file or directory."""
    # Escape the path for shell
    escaped_path = path.replace('"', '\\"')

    # Expand any ~ in the path
    cmd = f'eval echo "{escaped_path}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    expanded_path = stdout.read().decode().strip()

    # Escape the expanded path
    expanded_path = expanded_path.replace('"', '\\"')

    # Check if it's a file
    cmd = f'if [ -f "$(eval echo "{expanded_path}")" ]; then stat --format=%s "$(eval echo "{expanded_path}")"; else echo "DIR"; fi'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode().strip()

    if result != "DIR":
        try:
            return int(result)
        except ValueError:
            return None

    # If it's a directory, get total size
    cmd = f'du -sb "$(eval echo "{expanded_path}")" | cut -f1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    try:
        size = int(stdout.read().decode().strip())
        return size
    except (ValueError, IndexError):
        return None


def _get_local_size(path):
    """Calculate total size of local file or directory."""
    path = os.path.expanduser(path)
    if os.path.isfile(path):
        return os.path.getsize(path)

    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total


def _perform_transfer(ssh, local_path, remote_path, instance_id, local_to_remote, progress, task):
    """Perform the actual SCP transfer with progress bar."""
    total_size = 0
    transferred_size = 0
    file_count = 0
    current_file = ""
    current_file_size = 0
    current_file_transferred = 0

    # Pre-calculate total size
    try:
        if local_to_remote:
            total_size = _get_local_size(local_path)
        else:
            total_size = _get_remote_size(ssh, remote_path)
    except Exception as e:
        click.echo(click.style(
            "Warning: Could not pre-calculate total size", fg="yellow"))
        total_size = None

    def progress_callback(filename, size, sent):
        nonlocal transferred_size, file_count, current_file, current_file_size, current_file_transferred

        if sent == 0:  # New file started
            file_count += 1
            current_file = os.path.basename(filename)
            current_file_size = size
            current_file_transferred = 0

            # Handle both bytes and string filenames
            display_filename = current_file.decode(
                'utf-8') if isinstance(current_file, bytes) else current_file

            if total_size is None:
                progress.update(
                    task,
                    description=f"File {file_count}: {display_filename} - {_format_size(0)}/{_format_size(size)}"
                )
            else:
                progress.update(
                    task,
                    description=f"File {file_count}: {display_filename} - {_format_size(0)}/{_format_size(size)}"
                )
        else:
            # Calculate the increment since last update
            increment = sent - current_file_transferred
            transferred_size += increment
            current_file_transferred = sent

            if total_size is not None:
                progress.update(task, completed=transferred_size)

            # Handle both bytes and string filenames
            display_filename = current_file.decode(
                'utf-8') if isinstance(current_file, bytes) else current_file

            progress.update(
                task,
                description=f"File {file_count}: {display_filename} - {_format_size(sent)}/{_format_size(current_file_size)}"
            )

    transport = ssh.get_transport()
    transport.use_compression(True)

    with SCPClient(transport, progress=progress_callback) as scp:
        if local_to_remote:
            scp.put(local_path, remote_path, recursive=True)
        else:
            scp.get(remote_path, local_path, recursive=True)

    return file_count, total_size


@cli.command(
    help="Log in to Thunder Compute, prompting the user to generate an API token at console.thundercompute.com. Saves the API token to ~/.thunder/token",
    hidden=INSIDE_INSTANCE,
)
def login():
    if not logging_in:
        auth.login()


@cli.command(
    help="Log out of Thunder Compute and deletes the saved API token",
    hidden=INSIDE_INSTANCE,
)
def logout():
    auth.logout()


@cli.command(hidden=True)
def creds():
    token = get_token()
    uid = utils.get_uid(token)
    click.echo(f'{token},{uid}')


@cli.command(
    help="Setup",
    hidden=True,
)
@click.option('-g', '--global', 'global_setup', is_flag=True, help='Perform global setup')
def setup(global_setup):
    if not IS_WINDOWS:
        setup_cmd.setup(global_setup, get_token())
    else:
        raise click.ClickException("Setup is not supported on Windows")


@cli.command(
    help="Modify a Thunder Compute instance's properties (CPU, GPU, storage)",
    hidden=INSIDE_INSTANCE,
)
@click.argument("instance_id", required=True)
@click.option('--vcpus', type=click.Choice(VCPUS_CHOICES),
              help='New number of vCPUs. Cost scales with vCPU count')
@click.option('--gpu', type=click.Choice(GPU_CHOICES),
              help='New GPU type: T4 (16GB, inference), A100 (40GB, training), A100XL (80GB, training), H100 (80GB, training)')
@click.option('--num-gpus', type=click.Choice(NUM_GPUS_CHOICES),
              help='New number of GPUs to request. Multiple GPUs increase costs proportionally')
@click.option("--disk-size-gb", type=int, metavar="SIZE_GB",
              help="New disk size in GB (max: 1024). Can only increase disk size")
def modify(instance_id, vcpus, gpu, num_gpus, disk_size_gb):
    """Modify properties of a Thunder Compute instance.

    For running instances, only disk size increases are allowed.
    For stopped instances, all properties can be modified.
    At least one modification option must be specified.
    """
    # Validate at least one option is provided
    if not any([vcpus, gpu, num_gpus, disk_size_gb, num_gpus]):
        raise click.ClickException(
            "At least one modification option (--vcpus, --gpu, --num-gpus, or --disk-size-gb) must be specified"
        )

    token = get_token()
    success, error, instances = utils.get_instances(token)
    if not success:
        if "Unauthorized" in error:
            raise click.ClickException(
                UNAUTHORIZED_ERROR
            )
        else:
            raise click.ClickException(
                f"Failed to list Thunder Compute instances: {error}")

    metadata = instances.get(instance_id)
    if not metadata:
        raise click.ClickException(f"Instance {instance_id} not found")

    is_running = metadata["status"] != "STOPPED"
    is_pending = metadata["status"] == "PENDING"

    if is_pending:
        raise click.ClickException(
            "Instance is pending. Please wait for the previous operation to complete.")

    # Validate disk size changes
    if disk_size_gb:
        current_size = int(metadata["storage"])
        if current_size >= disk_size_gb:
            raise click.ClickException(
                f"Current disk size ({current_size}GB) is already greater than or equal to requested size ({disk_size_gb}GB)")
        if disk_size_gb > 1024:
            raise click.ClickException(
                f"The requested size ({disk_size_gb}GB) exceeds the 1TB limit")

    # For running instances, only allow disk resize and GPU changes
    if is_running:
        if vcpus:
            raise click.ClickException(
                "Cannot modify running instances. Stop your instance with `tnr stop` and retry.")
        if not any([disk_size_gb, gpu, num_gpus]):
            raise click.ClickException("No modifications specified")

    # For stopped instances, validate no duplicate changes
    if gpu and metadata["gpuType"] == gpu:
        raise click.ClickException(
            "GPU type is already the same as the requested GPU type")
    if num_gpus and int(metadata["numGpus"]) == int(num_gpus):
        raise click.ClickException(
            "Number of GPUs is already the same as the requested number of GPUs")
    if vcpus and int(metadata["cpuCores"]) == int(vcpus):
        raise click.ClickException(
            "Number of vCPUs is already the same as the requested number of vCPUs")

    # Prepare modification payload
    payload = {}
    if vcpus:
        payload['cpu_cores'] = int(vcpus)
    if gpu:
        payload['gpu_type'] = gpu
    if num_gpus:
        payload['num_gpus'] = int(num_gpus)
    if disk_size_gb:
        payload['disk_size_gb'] = disk_size_gb

    # Show confirmation message
    message = [
        "[yellow]This action will modify the instance's properties to:[/yellow]",
        f"[cyan]- {vcpus} vCPUs" if vcpus else None,
        f"[cyan]- {gpu.upper()} GPU" if gpu else None,
        f"[cyan]- {num_gpus} GPU{'s' if num_gpus != '1' else ''}" if num_gpus else None,
        f"[cyan]- {disk_size_gb}GB disk size" if disk_size_gb else None,
    ]
    panel = Panel(
        "\n".join([line for line in message if line]),
        highlight=True,
        width=100,
        box=box.ROUNDED,
    )
    rich.print(panel)
    if not click.confirm("Would you like to continue?"):
        click.echo(click.style(
            "The operation has been cancelled. No changes to the instance have been made.",
            fg="cyan",
        ))
        return

    # If instance is running and we're resizing disk, establish SSH connection
    ssh = None
    with DelayedProgress(
        SpinnerColumn(spinner_name="dots", style="white"),
        TextColumn("[white]{task.description}"),
        transient=True
    ) as progress:
        # Create a single task that we'll update
        task = progress.add_task("Modifying instance", total=None)

        success, error, _ = utils.modify_instance(instance_id, payload, token)

        if success and is_running and disk_size_gb:
            ip = metadata["ip"]
            if not ip:
                raise click.ClickException(
                    f"Instance {instance_id} has no valid IP")

            keyfile = utils.get_key_file(metadata["uuid"])
            if not os.path.exists(keyfile):
                if not utils.add_key_to_instance(instance_id, token):
                    raise click.ClickException(
                        f"Unable to find or create SSH key file for instance {instance_id}")

            # Establish SSH connection with retries
            start_time = time.time()
            connection_successful = False
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            while time.time() - start_time < 60:
                try:
                    timeout = 10 if platform.system() == 'Darwin' else None
                    ssh.connect(ip, username="ubuntu",
                                key_filename=keyfile, allow_agent=False, look_for_keys=False, timeout=timeout)
                    connection_successful = True
                    break
                except Exception:
                    time.sleep(5)

            if not connection_successful:
                raise click.ClickException(
                    "Failed to connect to the instance within a minute. Please retry or contact support@thundercompute.com if the issue persists"
                )

            # Update task description while waiting for instance
            progress.update(
                task, description="Waiting for instance to be ready")
            while True:
                _, _, instances = utils.get_instances(token)
                if instances[instance_id]["status"] != "PENDING":
                    break
                time.sleep(1)

            # Update task description for disk resize
            progress.update(task, description="Resizing disk")
            _, stdout, stderr = ssh.exec_command("""
                sudo apt install -y cloud-guest-utils
                sudo growpart /dev/sda 1
                sudo resize2fs /dev/sda1
            """)
            stdout.read().decode()
            stderr.read().decode()

        if ssh:
            ssh.close()

        if success:
            progress.stop()
            if not is_running and disk_size_gb:
                click.echo(click.style(
                    "Successfully queued instance modification! Check your instance with `tnr status`", fg="cyan"))
            else:
                click.echo(click.style(
                    "Successfully modified instance!", fg="cyan"))
        else:
            raise click.ClickException(f"Failed to modify instance: {error}")


@cli.command(
    help="Manage instance snapshots: create, list, or delete.",  # Updated help
    hidden=INSIDE_INSTANCE,
)
@click.argument("instance_id", type=int, required=False)
@click.argument("snapshot_name", type=str, required=False)
# Renamed variable
@click.option('--list', 'list_flag', is_flag=True, help='List all snapshots.')
# Renamed variable
@click.option('--delete', 'delete_name', type=str, help='Delete a snapshot by name.')
def snapshot(instance_id, snapshot_name, list_flag, delete_name):
    """Create a snapshot from a stopped instance, list snapshots, or delete a snapshot.

    - To CREATE: `tnr snapshot <INSTANCE_ID> <SNAPSHOT_NAME>`
    - To LIST:   `tnr snapshot --list`
    - To DELETE: `tnr snapshot --delete <SNAPSHOT_NAME>`

    These operations are mutually exclusive.
    """
    # Determine active modes
    is_list_mode = list_flag
    is_delete_mode = delete_name is not None
    # Create mode requires both instance_id and snapshot_name arguments
    has_create_args = instance_id is not None and snapshot_name is not None

    # --- Validate Exclusivity ---
    if is_list_mode and is_delete_mode:
        raise click.ClickException("Cannot use --list and --delete together.")
    if is_list_mode and (instance_id is not None or snapshot_name is not None):
        raise click.ClickException(
            "Cannot provide instance ID or snapshot name when using --list.")
    if is_delete_mode and (instance_id is not None or snapshot_name is not None):
        raise click.ClickException(
            "Cannot provide instance ID or snapshot name when using --delete.")

    # --- Action Handling ---
    token = get_token()  # Get token once, it's needed for all actions

    # Delete template info cache to ensure we get the latest template info
    utils.delete_template_info_cache()

    # LIST Action
    if is_list_mode:
        console = Console()
        current_snapshots = None
        final_table = None
        # Start with the loading state table
        initial_table = _create_snapshot_table(
            [], show_timestamp=True, loading=True)

        try:
            # Use Live to manage the updating table display
            with Live(initial_table, refresh_per_second=4, transient=True) as live:
                current_snapshots = _fetch_snapshot_data(
                    token)  # Initial fetch
                while True:
                    pending = _snapshots_pending(current_snapshots)
                    # Determine if the state has 'changed' to non-pending
                    # Pass changed=True when pending is False to update the caption correctly
                    table = _create_snapshot_table(
                        current_snapshots, show_timestamp=True, changed=not pending)
                    final_table = table  # Keep track of the last table state
                    live.update(table)  # Update the display

                    if not pending:
                        break  # Exit loop if no snapshots are pending

                    time.sleep(5)  # Wait before polling again
                    new_snapshots = _fetch_snapshot_data(token)

                    # Update if the list content or readiness has changed
                    if new_snapshots != current_snapshots:
                        current_snapshots = new_snapshots
                        # Check pending status again after update
                        if not _snapshots_pending(current_snapshots):
                            # If no longer pending, update table one last time with changed=True and break
                            table = _create_snapshot_table(
                                current_snapshots, show_timestamp=True, changed=True)
                            final_table = table
                            live.update(table)
                            break
                    # If no change, loop continues

        except KeyboardInterrupt:
            pass

        # Print the final state of the table after the loop/interruption
        if final_table:
            console.print(final_table)
        # Handle case where initial fetch might have failed or loop was interrupted early
        elif current_snapshots is None:
            console.print("Could not retrieve snapshot status.")
        # Handle case where there are no snapshots at all
        elif not current_snapshots:
            # Use create_snapshot_table to display the empty state correctly
            empty_table = _create_snapshot_table([])
            if empty_table:  # Check if it returned a table or None
                console.print(empty_table)
            else:
                # This message might be redundant if create_snapshot_table handles empty display well
                console.print("No Thunder Compute snapshots found.")

    # DELETE Action
    elif is_delete_mode:
        # Validate snapshot name format for delete
        if not re.match(r'^[a-z0-9-]+$', delete_name):
            raise click.ClickException(
                "Snapshot name for --delete can only contain lowercase letters, numbers, and hyphens.")

        click.echo(click.style(
            # User feedback
            f"Attempting to delete snapshot '{delete_name}'...", fg="cyan"))
        if utils.delete_snapshot(delete_name, token):
            click.echo(click.style(
                f"Successfully deleted snapshot '{delete_name}'.", fg="green"))
        else:
            # Improve error message if possible (e.g., distinguish not found vs other error)
            raise click.ClickException(
                f"Failed to delete snapshot '{delete_name}'. Does the snapshot exist or do you have permissions?")

    # CREATE Action (or invalid arguments)
    else:  # Neither list nor delete flag was used
        if has_create_args:
            # This is the explicit create case
            # Validate snapshot name format for create
            if not re.match(r'^[a-z0-9-]{1,62}$', snapshot_name):
                raise click.ClickException(
                    "Snapshot name can only contain lowercase letters, numbers, and hyphens (max 62 characters).")

            # Validate user and instance state
            success, error, instances = utils.get_instances(token)
            if not success:
                if "Unauthorized" in error:
                    raise click.ClickException(UNAUTHORIZED_ERROR)
                else:
                    raise click.ClickException(
                        f"Failed to get instance details: {error}")

            instance_id_str = str(instance_id)
            if instance_id_str not in instances:
                raise click.ClickException(
                    f"Instance with ID {instance_id} not found.")

            if instances[instance_id_str]["status"] != "STOPPED":
                raise click.ClickException(
                    f"Instance {instance_id} must be stopped to create a snapshot. Use `tnr stop {instance_id}` and try again.")

            # Call create snapshot utility
            click.echo(click.style(
                f"Creating snapshot '{snapshot_name}' from instance {instance_id}...", fg="cyan"))
            success, response = utils.make_snapshot(
                token, snapshot_name, instances[instance_id_str]["name"])
            if success:
                click.echo(click.style(
                    "Successfully initiated snapshot creation.", fg="green"))
                # Start list command
                click.echo('\n')
                ctx = click.get_current_context()
                ctx.invoke(snapshot, list_flag=True)
            else:
                # Consider more specific error from make_snapshot if available
                if "already exists" in response:
                    raise click.ClickException(
                        f"Snapshot with name '{snapshot_name}' already exists. Please choose a different name.")
                else:
                    raise click.ClickException(
                        f"Failed to initiate snapshot creation. An error occurred on the backend:\n {response}")

        elif instance_id is not None or snapshot_name is not None:
            # Called with partial create args, e.g. `tnr snapshot 123` or `tnr snapshot my-snap`
            raise click.ClickException(
                "Both instance ID and snapshot name are required to create a snapshot.")

        else:
            # Called with no args/flags, e.g., `tnr snapshot`
            ctx = click.get_current_context()
            click.echo(ctx.get_help())  # Show help message
            ctx.exit()  # Exit cleanly after showing help


def _fetch_snapshot_data(token):
    snap_success, snap_error, snaps = utils.get_snapshots(token)
    if not snap_success:
        if "Unauthorized" in snap_error:
            raise click.ClickException(
                f"Could not fetch snapshots: {UNAUTHORIZED_ERROR}"
            )
        else:
            raise click.ClickException(
                f"List snapshots failed with error: {snap_error}"
            )
    return snaps


def _snapshots_pending(snaps):
    if not snaps:
        return False
    # Check if any snapshot's 'ready' field is False
    return any(not snap.get("ready", False) for snap in snaps)

# Modified create_snapshot_table to handle loading/timestamp states


def _create_snapshot_table(snapshots, show_timestamp=False, changed=False, loading=False):
    snapshots_table = Table(
        title="Thunder Compute Snapshots",
        title_style="bold cyan",
        title_justify="left",
        box=box.ROUNDED,
    )

    snapshots_table.add_column("Name", justify="center")
    snapshots_table.add_column("Status", justify="center")
    snapshots_table.add_column("Base Template", justify="center")
    snapshots_table.add_column("Base GPU", justify="center")
    snapshots_table.add_column("Base Storage", justify="center")
    snapshots_table.add_column("Archive Size", justify="center")
    if loading:
        snapshots_table.add_row(
            "...",
            Text("LOADING", style="cyan"),
            "...",
            "...",
            "...",
            "..."
        )
    elif snapshots:
        for snapshot in snapshots:
            # Use Text objects for status with color styling
            status_text = Text("READY", style="green") if snapshot.get(
                "ready", False) else Text("PENDING", style="yellow")
            snapshots_table.add_row(
                str(snapshot.get("displayName", "--")),
                status_text,
                str(snapshot.get("defaultSpecs", {}).get("template", "--")),
                str(snapshot.get("defaultSpecs", {}).get(
                    "gpuType", "--")).upper(),
                f"{str(int(snapshot.get('defaultSpecs', {}).get('storage', '--')))}GB",
                f"{str(int(snapshot.get('archiveSize', 0)))}GB" if snapshot.get(
                    "archiveSize") else "--"
            )
    # Only add the empty row if not loading and the list is actually empty
    elif not loading:
        snapshots_table.add_row("--", "--", "--", "--", "--", "--")

    # Add caption with timestamp and status message if requested
    if show_timestamp:
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        # Adjust status message based on 'changed' and 'loading' flags
        status_msg = "All snapshots ready. Monitoring stopped." if changed and not loading else "Press Ctrl+C to stop monitoring"
        if loading:
            status_msg = "Loading initial snapshot state..."
        snapshots_table.caption = f"Last updated: {timestamp}\n{status_msg}"
        snapshots_table.caption_style = "dim"

    # Return the table object. The caller (Live context or direct print) handles display.
    if not snapshots and not loading and not show_timestamp:
        return None

    return snapshots_table


@cli.command(help="Check for and apply updates to the Thunder CLI.")
def update():
    """Checks for updates and attempts to install the latest version."""
    is_binary = getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')
    click.echo("Checking for updates...")

    meets_min, is_latest, details = utils.check_cli_up_to_date(
        force_check=True)

    if is_latest:
        current_version_info = ""
        if is_binary:
            # If latest, details will be None, so get current hash directly
            try:
                current_hash = utils.calculate_sha256(sys.executable)
                if current_hash:
                    current_version_info = f"(current hash: {current_hash[:12]}...)"
            except Exception:
                pass  # Ignore errors fetching hash
        else:  # Pip install
            try:
                # If latest, details might be None, get version directly
                current_version = version(PACKAGE_NAME)
                current_version_info = f"(current version: {current_version})"
            except Exception:
                pass  # Ignore if pip version cannot be determined

        # Fallback to using details if we couldn't get info directly (e.g., hash failed)
        if not current_version_info:
            if is_binary and details and details[0] == 'hash':
                # This case shouldn't normally happen if is_latest=True, but as a fallback
                current_version_info = f"(current hash: {details[1][:12]}...)"
            elif not is_binary and details and details[0] == 'version':
                current_version_info = f"(current version: {details[1]})"

        click.echo(click.style(
            f"✅ You are already running the latest version {current_version_info}.", fg="green"))
        sys.exit(0)

    update_type = "Mandatory" if not meets_min else "Optional"
    click.echo(click.style(f"{update_type} update available.", fg="yellow"))

    if is_binary:
        expected_hash = details[2] if details and details[0] == 'hash' else None
        if not expected_hash:
            # Attempt to re-fetch if details were missing hash initially
            is_latest_refetch, hash_details = utils.check_binary_hash()
            if not is_latest_refetch and hash_details and hash_details[0] == 'hash':
                expected_hash = hash_details[2]
            else:
                click.echo(click.style(
                    "Could not determine the required update hash. Please download manually from https://console.thundercompute.com/?download", fg="red"))
                sys.exit(1)

        click.echo(click.style("Attempting automatic update...", fg="cyan"))
        # Force update attempt, ignoring optional cache
        update_result = utils.attempt_binary_self_update(expected_hash)
        # Write cache only after a *manual* update attempt, to reset timer
        utils.write_optional_update_cache()

        if update_result is True:
            click.echo(click.style(
                "Update successful! Please re-run your command.", fg="green"))
            sys.exit(0)
        elif update_result == 'pending_restart':
            click.echo(click.style(
                "Update downloaded. Please exit and re-run your command.", fg="green"))
            sys.exit(0)
        else:
            click.echo(click.style("Automatic update failed.", fg="red"))
            click.echo(click.style(
                "Please download the latest version from https://console.thundercompute.com/?download", fg="cyan"))
            sys.exit(1)

    else:  # Pip install
        if details and details[0] == 'version':
            _, current_version, required_version = details
            click.echo(
                f'Your tnr version ({current_version}) is outdated. Latest/Required version is {required_version}.')
        else:
            # Try to get current version if details were missing it
            try:
                current_version = version(PACKAGE_NAME)
                click.echo(
                    f'Your tnr version ({current_version}) is outdated.')
            except Exception:
                click.echo("Your tnr version is outdated.")

        click.echo(click.style(
            'Please run "pip install --upgrade tnr" to update.', fg="cyan"))
        sys.exit(0)  # Exit cleanly, user needs to run pip


if __name__ == "__main__":
    cli()
