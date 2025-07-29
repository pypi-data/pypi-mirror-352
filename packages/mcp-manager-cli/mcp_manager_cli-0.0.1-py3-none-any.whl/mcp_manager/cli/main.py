import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import httpx
import subprocess
import signal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
import shlex
from prompt_toolkit.styles import Style
from mcp_manager.server.globals import settings
import shutil

API_URL = "http://localhost:4123"
CACHE_DIR = ".cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
PID_FILE = os.path.join(CACHE_DIR, "mcp_manager_daemon.pid")
API_KEY_FILE = os.path.join(CACHE_DIR, "mcp_manager_api_key.txt")
LOG_FILE = os.path.join(CACHE_DIR, "mcp_manager_daemon.log")
API_KEY = None

console = Console()

def load_api_key():
    global API_KEY
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            API_KEY = f.read().strip()
    else:
        API_KEY = None

# Load API key at startup
load_api_key()

def get_api_key():
    return API_KEY

def get_auth_headers():
    api_key = get_api_key()
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}

def cli():
    if len(sys.argv) == 1:
        ascii_art = r"""
[bold yellow]
  __  __  ___ ___   __  __                             
 |  \/  |/ __| _ \ |  \/  |__ _ _ _  __ _ __ _ ___ _ _ 
 | |\/| | (__|  _/ | |\/| / _` | ' \/ _` / _` / -_) '_|
 |_|  |_|\___|_|   |_|  |_|\__,_|_||_\__,_\__, \___|_|  
                                         |___/          CloudThinker
[/bold yellow]
"""
        console.print(ascii_art)
        console.print("[bold cyan]MCP Manager: Multi MCP Server Control Panel. Powered by CloudThinker (https://www.cloudthinker.io).[/bold cyan]")
        console.print("[white]Type 'help' for commands, 'exit' to quit.[/white]")
        style = Style.from_dict({
            'prompt': 'bold fg:ansigreen',
        })
        session = PromptSession()
        while True:
            try:
                cmd = session.prompt([('class:prompt', 'mcp-manager> ')], style=style)
                cmd = cmd.strip()
                if not cmd:
                    continue
                if cmd in ("exit", "quit"):
                    break
                if cmd in ("clear", "cls"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                if cmd == "help":
                    console.print(Panel.fit("""
[bold]Available commands:[/bold]
[cyan]  daemon start [--port PORT][/cyan]  Start the MCP Manager daemon (optionally on a custom port)
[cyan]  daemon stop[/cyan]          Stop the MCP Manager daemon
[cyan]  daemon status[/cyan]        Show daemon status
[cyan]  daemon log[/cyan]           Show the last N lines of the daemon log file
[cyan]  server list[/cyan]          List all managed servers
[cyan]  server reload[/cyan]        Reload the MCP servers from the config file
[cyan]  server remove <name>[/cyan]
[cyan]  server start <name>[/cyan]
[cyan]  server stop <name>[/cyan]
[cyan]  tools list[/cyan]           List all tools
[cyan]  api-key[/cyan]              Show the current API key
[cyan]  regenerate-api-key[/cyan]   Regenerate and show a new API key
[cyan]  config edit[/cyan]          Edit the MCP config JSON in vim
[cyan]  clear[/cyan]                Clear the screen
[cyan]  exit[/cyan]                 Exit the CLI

[bold yellow]Note:[/bold yellow] [white]`daemon start` runs the server on port 4123 by default. Use [cyan]--port <PORT>[/cyan] to specify a different port.[/white]
""", title="[bold magenta]MCP Manager Help[/bold magenta]"))
                    continue
                if cmd == "api-key":
                    print_api_key()
                    continue
                if cmd == "regenerate-api-key":
                    regenerate_api_key_cli()
                    continue
                if cmd == "config edit":
                    edit_config_vim()
                    continue
                # Parse and dispatch commands
                tokens = shlex.split(cmd)
                try:
                    if tokens[:2] == ["daemon", "start"]:
                        port = None
                        if "--port" in tokens:
                            try:
                                idx = tokens.index("--port")
                                port = int(tokens[idx + 1])
                            except Exception:
                                console.print("[yellow]Usage:[/yellow] daemon start [--port PORT]")
                                continue
                        try:
                            start_daemon(port=port)
                        except SystemExit:
                            pass
                        except Exception as e:
                            console.print(f"[red]Error:[/red] {e}")
                    elif tokens[:2] == ["daemon", "stop"]:
                        try:
                            stop_daemon()
                        except SystemExit:
                            pass
                        except Exception as e:
                            console.print(f"[red]Error:[/red] {e}")
                    elif tokens[:2] == ["daemon", "status"]:
                        daemon_status()
                    elif tokens[:2] == ["daemon", "log"]:
                        # Support: daemon log [--lines N]
                        lines = 40
                        if "--lines" in tokens:
                            try:
                                idx = tokens.index("--lines")
                                lines = int(tokens[idx + 1])
                            except Exception:
                                console.print("[yellow]Usage:[/yellow] daemon log [--lines N]")
                                continue
                        show_daemon_log(lines)
                    elif tokens[:2] == ["server", "reload"]:
                        do_reload_servers()
                    elif tokens[:2] == ["server", "list"]:
                        list_servers()
                    elif tokens[:2] == ["server", "remove"] and len(tokens) == 3:
                        do_server_remove(tokens[2])
                    elif tokens[:2] == ["server", "start"] and len(tokens) == 3:
                        do_server_start(tokens[2])
                    elif tokens[:2] == ["server", "stop"] and len(tokens) == 3:
                        do_server_stop(tokens[2])
                    elif tokens[:2] == ["tools", "list"]:
                        list_tools()
                    else:
                        console.print("[red]Unknown command.[/red] Type 'help' for a list of commands.")
                except SystemExit:
                    pass
                except Exception as e:
                    console.print(f"[red]Error:[/red] {e}")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[bold]Exiting MCP Manager CLI.[/bold]")
                break

def start_daemon(port=None):
    """Start the MCP Manager daemon (background FastAPI server)"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if os.path.exists(PID_FILE):
        console.print("[yellow]Daemon already running (PID file exists). Stop it first if needed.[/yellow]")
        return
    with open(os.devnull, "w") as devnull:
        cmd = ["mcp-manager-daemon"]
        if port:
            cmd += ["--port", str(port)]
            global API_URL
            API_URL = f"http://localhost:{port}"
        proc = subprocess.Popen(
            cmd,
            stdout=devnull,
            stderr=devnull,
            close_fds=True
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        port_info = f" on port {port}" if port else " on port 4123"
        console.print(Panel(f"MCP Manager daemon started [green](PID: {proc.pid})[/green]{port_info}", title="[bold cyan]Daemon Started[/bold cyan]"))

def stop_daemon():
    """Stop the MCP Manager daemon (background FastAPI server)"""
    if not os.path.exists(PID_FILE):
        console.print("[yellow]No daemon PID file found. Is the daemon running?[/yellow]")
        return
    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        console.print(f"[green]Sent SIGTERM to MCP Manager daemon (PID: {pid})[/green]")
    except ProcessLookupError:
        console.print(f"[yellow]No process with PID {pid} found. Removing stale PID file.[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to stop daemon:[/red] {e}")
    os.remove(PID_FILE)

def show_daemon_log(lines):
    """Show the last N lines of the daemon log file."""
    if not os.path.exists(LOG_FILE):
        console.print(Panel("No daemon log file found.", title="[bold red]Daemon Log[/bold red]"))
        return
    with open(LOG_FILE, "r") as f:
        log_lines = f.readlines()
    if not log_lines:
        console.print(Panel("Daemon log is empty.", title="[bold yellow]Daemon Log[/bold yellow]"))
        return
    tail = log_lines[-lines:]
    syntax = Syntax("".join(tail), "text", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[bold cyan]Daemon Log (last {lines} lines)[/bold cyan]"))

def daemon_status():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = f.read().strip()
        console.print(Panel(f"Daemon is running [green](PID: {pid})[/green]", title="[bold green]Daemon Status[/bold green]"))
    else:
        console.print(Panel("Daemon is not running.", title="[bold red]Daemon Status[/bold red]"))

def list_servers():
    r = httpx.get(f"{API_URL}/servers", headers=get_auth_headers())
    data = r.json()
    if isinstance(data, list) and data:
        table = Table(title="Managed Servers")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        for srv in data:
            table.add_row(str(srv.get("name", "")), str(srv.get("status", "")))
        console.print(table)
    else:
        console.print("[yellow]No servers found.[/yellow]")

def do_server_stop(name):
    r = httpx.post(f"{API_URL}/servers/{name}/stop", headers=get_auth_headers())
    resp = r.json()
    if r.status_code == 200:
        console.print(Panel(f"Server [bold green]{name}[/bold green] stopped.", title="[bold yellow]Server Stopped[/bold yellow]"))
    else:
        console.print(f"[red]Failed to stop server:[/red] {resp}")

def do_reload_servers():
    """Reload the MCP servers from the config file via the daemon API."""
    try:
        r = httpx.post(f"{API_URL}/servers/reload", headers=get_auth_headers())
        if r.status_code == 200:
            console.print(Panel("Servers reloaded from config.", title="[bold green]Servers Reloaded[/bold green]"))
        else:
            try:
                resp = r.json()
            except Exception:
                resp = r.text
            console.print(f"[red]Failed to reload servers:[/red] {resp}")
    except Exception as e:
        console.print(f"[red]Error reloading servers:[/red] {e}")

def do_server_start(name):
    r = httpx.post(f"{API_URL}/servers/{name}/start", headers=get_auth_headers())
    resp = r.json()
    if r.status_code == 200:
        console.print(Panel(f"Server [bold green]{name}[/bold green] started.", title="[bold green]Server Started[/bold green]"))
    else:
        console.print(f"[red]Failed to start server:[/red] {resp}")

def do_server_remove(name):
    r = httpx.delete(f"{API_URL}/servers/{name}", headers=get_auth_headers())
    resp = r.json()
    if r.status_code == 200:
        console.print(Panel(f"Server [bold green]{name}[/bold green] removed.", title="[bold cyan]Server Removed[/bold cyan]"))
    else:
        console.print(f"[red]Failed to remove server:[/red] {resp}")

def list_tools():
    r = httpx.get(f"{API_URL}/tools", headers=get_auth_headers())
    data = r.json()
    if isinstance(data, list) and data:
        table = Table(title="Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="magenta")
        for tool in data:
            table.add_row(str(tool.get("name", "")), str(tool.get("description", "")))
        console.print(table)
    else:
        console.print("[yellow]No tools found.[/yellow]")

def print_api_key():
    api_key = get_api_key()
    if api_key:
        console.print(f"[bold green]Current API Key:[/bold green] {api_key}")
    else:
        console.print("[red]API key not found.[/red]")

def regenerate_api_key_cli():
    try:
        r = httpx.post(f"{API_URL}/servers/regenerate-api-key", headers=get_auth_headers())
        if r.status_code == 200:
            new_key = r.json().get("api_key")
            if new_key:
                global API_KEY
                API_KEY = new_key
                console.print(f"[bold green]New API Key:[/bold green] {new_key}")
            else:
                console.print("[red]Failed to get new API key from server.[/red]")
        else:
            try:
                resp = r.json()
            except Exception:
                resp = r.text
            console.print(f"[red]Failed to regenerate API key:[/red] {resp}")
    except Exception as e:
        console.print(f"[red]Error regenerating API key:[/red] {e}")

def edit_config_vim():
    """Open the MCP config JSON file in the user's editor (vim, notepad, or $EDITOR).
    After editing, checks if the file is valid JSON. If not, prompts user to re-edit.
    """
    import json

    config_path = settings.MCP_CONFIG
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"mcpServers": {}}, f, indent=2)

    editor = os.environ.get("EDITOR")
    if editor and shutil.which(editor):
        edit_cmd = f'{editor} "{config_path}"'
    elif os.name == "nt":
        edit_cmd = f'notepad "{config_path}"'
    elif shutil.which("vim"):
        edit_cmd = f"vim '{config_path}'"
    elif shutil.which("nano"):
        edit_cmd = f"nano '{config_path}'"
    else:
        console.print("[red]No suitable editor found. Please set the EDITOR environment variable.[/red]")
        return

    while True:
        os.system(edit_cmd)
        # After editing, check if the file is valid JSON
        try:
            with open(config_path, "r") as f:
                json.load(f)
            console.print("[green]Config file is valid JSON.[/green]")
            break
        except Exception as e:
            console.print(f"[red]Config file is not valid JSON![/red] Error: {e}")
            console.print("[yellow]Please fix the JSON and save again. The editor will reopen.[/yellow]")

if __name__ == "__main__":
    cli() 