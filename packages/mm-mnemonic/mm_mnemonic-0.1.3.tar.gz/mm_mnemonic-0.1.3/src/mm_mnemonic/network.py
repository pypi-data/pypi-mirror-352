"""Network connectivity detection module.

This module provides functionality to detect internet connectivity
by attempting connections to multiple DNS servers concurrently.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import typer
from rich.console import Console


def _test_connection(host: str, port: int, timeout: float = 3.0) -> bool:
    """Test TCP connection to a specific host and port.

    Args:
        host: The hostname or IP address to connect to
        port: The port number to connect to
        timeout: Connection timeout in seconds

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, TimeoutError):
        return False


def has_internet_connection(timeout: float = 3.0) -> bool:
    """Check if internet connection is available.

    This function attempts to connect to multiple well-known DNS servers
    concurrently. If any connection succeeds, internet is considered available.

    Args:
        timeout: Connection timeout in seconds for each attempt

    Returns:
        True if internet connection is detected, False otherwise
    """
    test_servers: list[tuple[str, int]] = [
        ("8.8.8.8", 53),  # Google DNS
        ("1.1.1.1", 53),  # Cloudflare DNS
        ("208.67.222.222", 53),  # OpenDNS
    ]

    # Use ThreadPoolExecutor to test all connections concurrently
    with ThreadPoolExecutor(max_workers=len(test_servers)) as executor:
        # Submit all connection tests
        future_to_server = {executor.submit(_test_connection, host, port, timeout): (host, port) for host, port in test_servers}

        # Check results as they complete
        for future in as_completed(future_to_server):
            if future.result():
                # If any connection succeeds, internet is available
                return True

    # All connections failed
    return False


def check_network_security(allow_internet_risk: bool) -> None:
    """Check network security and show warnings.

    Args:
        allow_internet_risk: Whether to allow running with internet connection

    Raises:
        typer.Exit: If internet is detected and allow_internet_risk is False
    """
    if has_internet_connection():
        console = Console()

        if not allow_internet_risk:
            console.print()
            console.print("🚨 [bold red]SECURITY WARNING: Internet connection detected![/bold red]")
            console.print()
            console.print("Your mnemonic and private keys may be exposed to potential attacks.")
            console.print("For maximum security, disconnect from the internet before running this command.")
            console.print()
            console.print("To proceed anyway (NOT recommended), use: [bold cyan]--allow-internet-risk[/bold cyan]")
            console.print()
            raise typer.Exit(1)

        console.print()
        console.print("⚠️  [bold yellow]WARNING: Running with internet connection![/bold yellow]")
        console.print("Your mnemonic may be exposed to potential attacks.")
        console.print("For maximum security, disconnect from internet.")
        console.print()
