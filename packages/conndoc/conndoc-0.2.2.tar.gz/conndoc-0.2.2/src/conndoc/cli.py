import socket
import datetime
import typer
import httpx
import time
import concurrent.futures

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.live import Live

from conndoc.validators import *

from conndoc.constants import (
    DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT_SECOND, DEFAULT_HTTP_URL
)

app = typer.Typer(no_args_is_help=True)

@app.callback()
def main():
    """
    conndoc: Diagnose connectivity issues using ping, dns, and more.
    """
    pass

@app.command()
def ping(
    host: str = typer.Argument(DEFAULT_HOST),
    timeout: float = typer.Option(DEFAULT_TIMEOUT_SECOND, help="Timeout per packet in seconds")
):
    try:
        validate_ping(host, timeout)
        print(f"[green]\u2714 Successfully pinged {host}[/green]")
    except FileNotFoundError:
        print("[red]\u274c Ping command not found on this system.[/red]")
        raise typer.Exit(code=1)
    except RuntimeError as e:
        print(f"[red]\u274c Ping failed: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def checkdns(host: str = typer.Argument(DEFAULT_HOST)):
    if is_ip(host):
        print(f"[yellow]\u26a0 DNS check is meant for domain names, but got an IP: {host}[/yellow]")
        return
    try:
        result = validate_dns(host)
        ips = sorted(set([item[4][0] for item in result]))
        for ip in ips:
            print(f"[green]\u2714[/green] {ip}")
    except socket.gaierror as e:
        print(f"[red]DNS resolution failed:[/red] {e}")
        raise typer.Exit(code=1)

@app.command()
def checkssl(host: str = typer.Argument(DEFAULT_HOST), port: int = typer.Argument(DEFAULT_PORT)):
    try:
        cert = validate_ssl(host, port)
    except Exception as e:
        print(f"[red]❌ Failed to retrieve SSL certificate: {e}[/red]")
        raise typer.Exit(code=1)

    now = datetime.datetime.now(datetime.timezone.utc)
    not_before = datetime.datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
    not_after = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
    remaining_days = (not_after - now).days

    subject = dict(x[0] for x in cert["subject"])
    issuer = dict(x[0] for x in cert["issuer"])

    status = "[green]✅ VALID[/green]" if now < not_after else "[red]❌ EXPIRED[/red]"

    print(Panel.fit(
        f"[bold]🔐 SSL Certificate for {host}:{port}[/bold]\n\n"
        f"[cyan]Subject CN:[/cyan] {subject.get('commonName', 'N/A')}\n"
        f"[cyan]Issuer:[/cyan] {issuer.get('organizationName', 'N/A')}\n"
        f"[cyan]Valid From:[/cyan] {not_before.strftime('%Y-%m-%d')}\n"
        f"[cyan]Valid To:[/cyan] {not_after.strftime('%Y-%m-%d')} ([bold]{remaining_days} days remaining[/bold])\n"
        f"[cyan]Status:[/cyan] {status}",
        title="SSL Diagnostic",
        border_style="blue"
    ))

@app.command()
def checkhttp(host: str = typer.Argument(DEFAULT_HTTP_URL)):
    try:
        start_time = time.time()
        response = validate_http(host)
        latency_ms = int((time.time() - start_time) * 1000)

        print(Panel.fit(
            f"[bold]\U0001f310 HTTP GET {response.url}[/bold]\n\n"
            f"[cyan]Status:[/cyan] {response.status_code} {response.reason_phrase}\n"
            f"[cyan]Latency:[/cyan] {latency_ms} ms\n"
            f"[cyan]Final URL:[/cyan] {response.url}\n\n"
            f"[cyan]Headers:[/cyan]\n" +
            "\n".join([f"[white]{k}[/white]: [green]{v}[/green]" for k, v in response.headers.items() if k.lower() in ("server", "content-type", "location")]),
            title="HTTP Diagnostic",
            border_style="green"
        ))

    except httpx.RequestError as e:
        print(f"[red]\u274c HTTP request failed: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def checktcp(
    host: str = typer.Argument(DEFAULT_HOST),
    port: int = typer.Argument(DEFAULT_PORT),
    timeout: float = typer.Option(DEFAULT_TIMEOUT_SECOND)
):
    try:
        validate_tcp(host, port, timeout)
        print(f"[green]\u2714 Successfully connected to {host}:{port}[/green]")
    except Exception as e:
        print(f"[red]\u274c TCP connection failed: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def summary(
    host: str = typer.Argument(DEFAULT_HOST),
    port: int = typer.Option(DEFAULT_PORT),
    timeout: float = typer.Option(DEFAULT_TIMEOUT_SECOND),
):
    console = Console()
    is_domain = not is_ip(host)

    checks = ["Ping"]
    if is_domain:
        checks += ["DNS", "SSL"]
    checks += ["HTTP", "TCP"]

    results = {check: "[yellow]\u23f3 Running...[/yellow]" for check in checks}

    def make_table():
        table = Table(title=f"[bold]{host}[/bold]", width=80)
        table.add_column("Check", no_wrap=True)
        table.add_column("Result", style="bold")
        for check in checks:
            table.add_row(check, results[check])
        return table

    check_to_command = {
        "Ping": "ping",
        "DNS": "checkdns",
        "SSL": "checkssl",
        "HTTP": "checkhttp",
        "TCP": "checktcp"
    }

    def safe_run(label, func):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func)
                future.result(timeout=DEFAULT_TIMEOUT_SECOND)
            results[label] = "[green]\u2714 PASS[/green]"
        except concurrent.futures.TimeoutError:
            cmd = check_to_command[label]
            results[label] = f"[red]\u274c FAIL[/red] — Timed out.\nTry [bold]conndoc {cmd} {host}[/bold]"
        except Exception as e:
            cmd = check_to_command[label]
            short_msg = str(e).split("\n")[0].strip()
            results[label] = f"[red]\u274c FAIL[/red] — {short_msg}.\nTry [bold]conndoc {cmd} {host}[/bold]"

    with Live(make_table(), console=console, refresh_per_second=8) as live:
        safe_run("Ping", lambda: validate_ping(host))
        live.update(make_table())

        if is_domain:
            safe_run("DNS", lambda: validate_dns(host))
            live.update(make_table())

            safe_run("SSL", lambda: validate_ssl(host, port, timeout))
            live.update(make_table())

        safe_run("HTTP", lambda: validate_http(host))
        live.update(make_table())

        safe_run("TCP", lambda: validate_tcp(host, port, timeout))
        live.update(make_table())

    if all("\u2714 PASS" in result for result in results.values()):
        console.print("[bold green]\u2705 All checks passed[/bold green]")
    else:
        console.print("[bold red]\u274c One or more checks failed[/bold red]")
