import dataclasses
from pathlib import Path

import tomlkit
import typer
from rich.console import Console
from rich.table import Table

from mm_mnemonic.account import DerivedAccounts
from mm_mnemonic.crypto import OpensslAes256Cbc


def store_derived_accounts(derived_accounts: DerivedAccounts, output_dir: Path, encryption_password: str | None) -> None:
    # output_dir can't be a file or be not empty
    if output_dir.is_file():
        raise ValueError("output_dir must be a directory, not a file")
    if output_dir.is_dir() and any(output_dir.iterdir()):
        raise ValueError(f"error: {output_dir} is not empty")

    output_dir.mkdir(parents=True, exist_ok=True)
    keys_file = output_dir / ("keys.toml" + (".enc" if encryption_password else ""))
    addresses_file = output_dir / "addresses.txt"

    keys_data = tomlkit.dumps(dataclasses.asdict(derived_accounts), sort_keys=False)
    if encryption_password is not None:
        cipher = OpensslAes256Cbc(password=encryption_password)
        keys_data = cipher.encrypt_base64(keys_data)

    keys_file.write_text(keys_data)
    addresses_file.write_text("\n".join(a.address for a in derived_accounts.accounts))


def print_derived_accounts(derived_accounts: DerivedAccounts, show_sensitive: bool = True) -> None:
    typer.echo("Coin: " + derived_accounts.coin.value)

    # Mnemonic: show word count instead of actual mnemonic when not showing sensitive info
    if show_sensitive:
        typer.echo("Mnemonic: " + derived_accounts.mnemonic)
    else:
        word_count = len(derived_accounts.mnemonic.split())
        typer.echo(f"Mnemonic: {word_count} words (saved to file)")

    # Passphrase: show presence instead of actual passphrase when not showing sensitive info
    if show_sensitive:
        typer.echo("Passphrase: " + derived_accounts.passphrase)
    else:
        has_passphrase = bool(derived_accounts.passphrase)
        passphrase_status = "yes (saved to file)" if has_passphrase else "no"
        typer.echo(f"Passphrase: {passphrase_status}")

    typer.echo("Derivation Path: " + derived_accounts.derivation_path)

    table = Table()
    table.add_column("Path")
    table.add_column("Address")

    # Only add Private Key column when showing sensitive information
    if show_sensitive:
        table.add_column("Private Key")
        for acc in derived_accounts.accounts:
            table.add_row(acc.path, acc.address, acc.private)
    else:
        for acc in derived_accounts.accounts:
            table.add_row(acc.path, acc.address)

    console = Console()
    console.print(table)
