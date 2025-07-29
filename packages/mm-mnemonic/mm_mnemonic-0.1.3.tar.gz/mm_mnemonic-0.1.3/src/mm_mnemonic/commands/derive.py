import sys
from pathlib import Path

import typer
from pydantic import BaseModel

from mm_mnemonic import output
from mm_mnemonic.account import derive_accounts
from mm_mnemonic.mnemonic import is_valid_mnemonic
from mm_mnemonic.network import check_network_security
from mm_mnemonic.passphrase import prompt_encryption_password
from mm_mnemonic.types import Coin


class Params(BaseModel):
    coin: Coin
    mnemonic: str | None
    passphrase: str | None
    derivation_path: str | None
    limit: int
    output_dir: Path | None
    encrypt: bool
    allow_internet_risk: bool

    def validate_params(self) -> None:
        # Encrypt validation
        if self.encrypt and self.output_dir is None:
            raise typer.BadParameter(
                "Cannot use --encrypt without --output-dir. Use --output-dir to specify where to save encrypted files."
            )


def run(params: Params) -> None:
    params.validate_params()
    try:
        check_network_security(params.allow_internet_risk)

        if params.mnemonic is None:
            # Interactive mode - prompt for both mnemonic and passphrase
            while True:
                mnemonic = typer.prompt("Mnemonic", hide_input=True)
                if is_valid_mnemonic(mnemonic):
                    break
                typer.echo("invalid mnemonic")
            passphrase = typer.prompt("Passphrase", hide_input=True, default="")
        else:
            # Direct mode - use provided mnemonic with optional passphrase
            mnemonic = params.mnemonic
            passphrase = params.passphrase or ""

        derived_accounts = derive_accounts(
            coin=params.coin,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=params.derivation_path,
            limit=params.limit,
        )

        if params.output_dir:
            encryption_password = None
            if params.encrypt:
                encryption_password = prompt_encryption_password()
            output.store_derived_accounts(derived_accounts, params.output_dir, encryption_password)

        # Don't show sensitive information on screen when saving to files
        show_sensitive = params.output_dir is None
        output.print_derived_accounts(derived_accounts, show_sensitive=show_sensitive)

    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes for security warnings
        raise
    except Exception as e:
        typer.echo(str(e))
        sys.exit(1)
