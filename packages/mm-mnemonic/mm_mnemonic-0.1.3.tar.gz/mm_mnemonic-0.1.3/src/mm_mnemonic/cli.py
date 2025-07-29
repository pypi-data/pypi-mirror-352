import importlib.metadata
from pathlib import Path
from typing import Annotated

import typer

from mm_mnemonic import commands
from mm_mnemonic.types import Coin

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, rich_markup_mode="rich")


def mnemonic_words_callback(value: int) -> int:
    if value not in [12, 15, 21, 24]:
        raise typer.BadParameter("Words must be one of: 12, 15, 21, 24")
    return value


@app.command(name="derive")
def derive_command(
    # Input options
    mnemonic: Annotated[
        str | None,
        typer.Option("--mnemonic", "-m", help="BIP39 mnemonic phrase (12-24 words). If not provided, will prompt interactively."),
    ] = None,
    passphrase: Annotated[
        str | None,
        typer.Option(
            "--passphrase",
            "-p",
            help="BIP39 passphrase (optional, only used with --mnemonic). "
            "If --mnemonic is provided but --passphrase is not, empty passphrase is used.",
        ),
    ] = None,
    # Cryptocurrency and derivation options
    coin: Annotated[Coin, typer.Option("--coin", "-c", help="Cryptocurrency to derive accounts for")] = Coin.ETH,
    derivation_path: Annotated[
        str | None,
        typer.Option(
            "--derivation-path",
            help="Custom derivation path template (e.g., m/44'/0'/0'/0/{i}). Uses coin-specific default if not specified.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Number of accounts to derive from the mnemonic", min=1)] = 10,
    # Output options
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to save account files (keys.toml and addresses.txt). "
            "If not specified, accounts are only displayed on screen.",
        ),
    ] = None,
    encrypt: Annotated[
        bool,
        typer.Option("--encrypt", "-e", help="Encrypt saved keys with AES-256-CBC (requires --output-dir)"),
    ] = False,
    # Security options
    allow_internet_risk: Annotated[
        bool,
        typer.Option(
            "--allow-internet-risk", help="Allow running with internet connection (SECURITY RISK: your mnemonic may be exposed)"
        ),
    ] = False,
) -> None:
    """
    Display cryptocurrency accounts derived from an existing BIP39 mnemonic

    [bold]INPUT MODES:[/bold]

    [italic]Interactive mode[/italic] (no --mnemonic):
        Prompts for both mnemonic and passphrase with hidden input

    [italic]Direct mode[/italic] (--mnemonic provided):
        Uses provided mnemonic with optional passphrase (empty if not specified)

    [bold]EXAMPLES:[/bold]

    [dim]# Interactive mode[/dim]
    [bold]mm-mnemonic derive --coin BTC --limit 5[/bold]

    [dim]# Use specific mnemonic without passphrase[/dim]
    [bold]mm-mnemonic derive --mnemonic "abandon abandon abandon..." --coin ETH[/bold]

    [dim]# Use mnemonic with passphrase and save to encrypted files[/dim]
    [bold]mm-mnemonic derive --mnemonic "..." --passphrase "secret" --output-dir ./keys --encrypt[/bold]

    [dim]# Custom derivation path[/dim]
    [bold]mm-mnemonic derive --derivation-path "m/44'/3'/0'/0/{i}" --limit 20[/bold]

    [reverse] SECURITY WARNING [/reverse]
    This command handles sensitive cryptographic material (mnemonic phrases).
    For maximum security, run on an air-gapped machine without internet.
    Use [bold]--allow-internet-risk[/bold] to bypass this check.
    """
    commands.derive.run(
        commands.derive.Params(
            coin=coin,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=derivation_path,
            limit=limit,
            output_dir=output_dir,
            encrypt=encrypt,
            allow_internet_risk=allow_internet_risk,
        )
    )


@app.command(name="new")
def new_command(
    # Generation options
    generate_passphrase: Annotated[
        bool, typer.Option("--generate-passphrase", "-g", help="Generate a random passphrase")
    ] = False,
    passphrase: Annotated[str | None, typer.Option("--passphrase", "-p", help="Specify a custom passphrase")] = None,
    prompt_passphrase: Annotated[
        bool, typer.Option("--prompt-passphrase", "-i", help="Interactively prompt for passphrase")
    ] = False,
    words: Annotated[
        int,
        typer.Option("--words", "-w", help="Number of words for generated mnemonic", callback=mnemonic_words_callback),
    ] = 24,
    # Cryptocurrency and derivation options
    coin: Annotated[Coin, typer.Option("--coin", "-c", help="Cryptocurrency to derive accounts for")] = Coin.ETH,
    derivation_path: Annotated[
        str | None,
        typer.Option(
            "--derivation-path",
            help="Custom derivation path template (e.g., m/44'/0'/0'/0/{i}). Uses coin-specific default if not specified.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Number of accounts to derive from the mnemonic", min=1)] = 10,
    # Output options
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to save account files (keys.toml and addresses.txt). "
            "If not specified, accounts are only displayed on screen.",
        ),
    ] = None,
    encrypt: Annotated[
        bool,
        typer.Option("--encrypt", "-e", help="Encrypt saved keys with AES-256-CBC (requires --output-dir)"),
    ] = False,
    # Security options
    allow_internet_risk: Annotated[
        bool,
        typer.Option(
            "--allow-internet-risk", help="Allow running with internet connection (SECURITY RISK: your mnemonic may be exposed)"
        ),
    ] = False,
) -> None:
    """
    Generate new cryptocurrency wallets with fresh BIP39 mnemonics

    [bold]PASSPHRASE OPTIONS:[/bold]

    [italic]No passphrase[/italic] (default):
        Generates mnemonic without passphrase

    [italic]Generate random passphrase[/italic]:
        [bold]--generate-passphrase[/bold] - creates secure random passphrase

    [italic]Specify custom passphrase[/italic]:
        [bold]--passphrase "mypassword"[/bold] - uses your custom passphrase

    [italic]Interactive passphrase input[/italic]:
        [bold]--prompt-passphrase[/bold] - prompts for passphrase with hidden input

    [bold]EXAMPLES:[/bold]

    [dim]# Generate mnemonic without passphrase[/dim]
    [bold]mm-mnemonic new --coin ETH[/bold]

    [dim]# Generate with random passphrase[/dim]
    [bold]mm-mnemonic new --generate-passphrase --coin BTC[/bold]

    [dim]# Use custom passphrase[/dim]
    [bold]mm-mnemonic new --passphrase "mysecret" --coin ETH[/bold]

    [dim]# Prompt for passphrase interactively[/dim]
    [bold]mm-mnemonic new --prompt-passphrase --coin SOL[/bold]

    [dim]# Generate 12-word mnemonic with encrypted output[/dim]
    [bold]mm-mnemonic new --words 12 --generate-passphrase --output-dir ./wallets --encrypt[/bold]

    [reverse] SECURITY WARNING [/reverse]
    This command generates sensitive cryptographic material (mnemonic phrases).
    For maximum security, run on an air-gapped machine without internet.
    Use [bold]--allow-internet-risk[/bold] to bypass this check.
    """
    commands.new.run(
        commands.new.Params(
            generate_passphrase=generate_passphrase,
            passphrase=passphrase,
            prompt_passphrase=prompt_passphrase,
            words=words,
            coin=coin,
            derivation_path=derivation_path,
            limit=limit,
            output_dir=output_dir,
            encrypt=encrypt,
            allow_internet_risk=allow_internet_risk,
        )
    )


@app.command(name="search")
def search_command(
    addresses: Annotated[
        list[str] | None, typer.Argument(help="Address patterns to search for (supports wildcards: 0x1234*, *abcd, *1234*)")
    ] = None,
    coin: Annotated[Coin, typer.Option("--coin", "-c", help="Cryptocurrency to search addresses for")] = Coin.ETH,
    addresses_file: Annotated[
        Path | None, typer.Option("--addresses-file", "-f", help="File containing address patterns (one per line)")
    ] = None,
    mnemonic: Annotated[
        str | None,
        typer.Option("--mnemonic", "-m", help="BIP39 mnemonic phrase (12-24 words). If not provided, will prompt interactively."),
    ] = None,
    passphrase: Annotated[
        str | None,
        typer.Option(
            "--passphrase",
            "-p",
            help="BIP39 passphrase (optional, use with --mnemonic). If not provided, will prompt interactively.",
        ),
    ] = None,
    derivation_path: Annotated[
        str | None,
        typer.Option(
            "--derivation-path",
            help="Custom derivation path template (e.g., m/44'/0'/0'/0/{i}). Default paths used if not specified.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum number of derivation paths to check")] = 1000,
    # Security options
    allow_internet_risk: Annotated[
        bool,
        typer.Option(
            "--allow-internet-risk", help="Allow running with internet connection (SECURITY RISK: your mnemonic may be exposed)"
        ),
    ] = False,
) -> None:
    """
    Search for specific addresses in derived accounts from BIP39 mnemonic

    Interactively prompts for mnemonic and passphrase, then searches through
    derived accounts to find matches for the specified address patterns.

    WILDCARD PATTERNS:

    0x1234*      Address starts with '0x1234'

    *abcd        Address ends with 'abcd'

    *1234*       Address contains '1234' anywhere

    0x1234abcd   Exact address match (no wildcards)


    USAGE EXAMPLES:

    # Search for specific addresses
    mm-mnemonic search 0x1234abcd 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

    # Search with wildcards
    mm-mnemonic search 0x1234* *abcd bc1q*

    # Search from file
    mm-mnemonic search --addresses-file addresses.txt

    # Combine arguments and file
    mm-mnemonic search 0x1234* --addresses-file more-addresses.txt

    # Search Bitcoin addresses with higher limit
    mm-mnemonic search 1A1zP1eP* --coin BTC --limit 5000

    # Custom derivation path
    mm-mnemonic search 0x1234* --derivation-path "m/44'/60'/0'/0/{i}"


    ADDRESS FILE FORMAT:

    One address pattern per line, empty lines and lines starting with # are ignored:

        # My lost addresses
        0x1234abcd*
        *5678efgh
        1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa


    SUPPORTED COINS: BTC, BTC_TESTNET, ETH, SOL, TRX

    SECURITY WARNING:
    This command handles sensitive cryptographic material (mnemonic phrases).
    For maximum security, run this command on an air-gapped machine without
    internet connection. Use --allow-internet-risk to bypass this check.
    """
    # Convert None to empty list for addresses
    if addresses is None:
        addresses = []

    commands.search.run(
        commands.search.Params(
            coin=coin,
            addresses=addresses,
            addresses_file=addresses_file,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=derivation_path,
            limit=limit,
            allow_internet_risk=allow_internet_risk,
        )
    )


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mm-mnemonic version: {importlib.metadata.version('mm-mnemonic')}")
        raise typer.Exit


@app.callback()
def main(
    _version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Print the version and exit"),
) -> None:
    pass


if __name__ == "__main__":
    app()
