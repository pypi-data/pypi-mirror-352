import sys
from pathlib import Path

import typer
from pydantic import BaseModel

from mm_mnemonic.account import derive_account, get_default_derivation_path, is_address_matched
from mm_mnemonic.mnemonic import is_valid_mnemonic
from mm_mnemonic.network import check_network_security
from mm_mnemonic.types import Coin


class Params(BaseModel):
    coin: Coin
    addresses: list[str]
    addresses_file: Path | None
    mnemonic: str | None
    passphrase: str | None
    derivation_path: str | None
    limit: int
    allow_internet_risk: bool  # Allow running with internet connection

    def validate_params(self) -> None:
        # Validate that we have at least one search pattern
        if not self.addresses and not self.addresses_file:
            raise typer.BadParameter("No addresses to search for. Provide addresses as arguments or use --addresses-file.")


class SearchResult(BaseModel):
    search_pattern: str
    address: str
    derivation_path: str


def _validate_mnemonic(mnemonic: str) -> None:
    """Validate mnemonic phrase and raise error if invalid."""
    if not is_valid_mnemonic(mnemonic):
        raise typer.BadParameter("Invalid mnemonic phrase")


def run(params: Params) -> None:
    params.validate_params()

    # Check network security first
    check_network_security(params.allow_internet_risk)

    try:
        # Get mnemonic and passphrase - from params or interactively
        if params.mnemonic:
            mnemonic = params.mnemonic
            _validate_mnemonic(mnemonic)
            passphrase = params.passphrase or ""
        else:
            # Interactive mode
            while True:
                mnemonic = typer.prompt("Mnemonic", hide_input=True)
                if is_valid_mnemonic(mnemonic):
                    break
                typer.echo("Invalid mnemonic")
            passphrase = typer.prompt("Passphrase", hide_input=True, default="")

        # Collect all search patterns
        search_patterns = collect_search_patterns(params.addresses, params.addresses_file)

        if not search_patterns:
            typer.echo("No address patterns found to search for.")
            sys.exit(1)

        # Get derivation path
        derivation_path = params.derivation_path or get_default_derivation_path(params.coin)

        # Perform search
        results = search_addresses(
            coin=params.coin,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=derivation_path,
            search_patterns=search_patterns,
            limit=params.limit,
        )

        # Display results
        display_search_results(results, params.coin, derivation_path, search_patterns)

    except Exception as e:
        typer.echo(str(e))
        sys.exit(1)


def collect_search_patterns(addresses: list[str], addresses_file: Path | None) -> list[str]:
    """Collect search patterns from arguments and file."""
    patterns = list(addresses)  # Copy from arguments

    if addresses_file:
        if not addresses_file.exists():
            raise typer.BadParameter(f"Addresses file not found: {addresses_file}")

        try:
            with addresses_file.open(encoding="utf-8") as f:
                for file_line in f:
                    stripped_line = file_line.strip()
                    # Skip empty lines and comments
                    if stripped_line and not stripped_line.startswith("#"):
                        patterns.append(stripped_line)
        except Exception as e:
            raise typer.BadParameter(f"Error reading addresses file: {e}") from e

    # Remove duplicates while preserving order
    seen = set()
    unique_patterns = []
    for pattern in patterns:
        if pattern not in seen:
            seen.add(pattern)
            unique_patterns.append(pattern)

    return unique_patterns


def search_addresses(
    coin: Coin,
    mnemonic: str,
    passphrase: str,
    derivation_path: str,
    search_patterns: list[str],
    limit: int,
) -> list[SearchResult]:
    """Search for addresses matching the given patterns."""
    results = []

    typer.echo(f"Searching through {limit} addresses for {len(search_patterns)} patterns...")

    for i in range(limit):
        # Derive account for this index
        path = derivation_path.replace("{i}", str(i))
        try:
            account = derive_account(coin, mnemonic, passphrase, path)
        except Exception as e:
            typer.echo(f"Error deriving account at {path}: {e}")
            continue

        # Check against all search patterns
        for pattern in search_patterns:
            if is_address_matched(account.address, pattern):
                results.append(
                    SearchResult(
                        search_pattern=pattern,
                        address=account.address,
                        derivation_path=path,
                    )
                )
                typer.echo(f"Found match for '{pattern}': {account.address} at {path}")

    return results


def display_search_results(results: list[SearchResult], coin: Coin, derivation_path: str, search_patterns: list[str]) -> None:
    """Display search results in a formatted table."""
    typer.echo()
    typer.echo("Search completed.")
    typer.echo(f"Coin: {coin}")
    typer.echo(f"Derivation Path Template: {derivation_path}")
    typer.echo(f"Search Patterns: {', '.join(search_patterns)}")
    typer.echo()

    if not results:
        typer.echo("No matches found.")
        return

    typer.echo(f"Found {len(results)} matches:")
    typer.echo()

    # Create beautiful table using rich (available through typer)
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    table.add_column("Search Pattern", style="cyan")
    table.add_column("Address", style="green")
    table.add_column("Derivation Path", style="yellow")

    for result in results:
        table.add_row(
            result.search_pattern,
            result.address,
            result.derivation_path,
        )

    console.print(table)
