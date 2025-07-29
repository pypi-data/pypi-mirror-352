import sys
from pathlib import Path

import typer
from pydantic import BaseModel

from mm_mnemonic import output
from mm_mnemonic.account import derive_accounts
from mm_mnemonic.mnemonic import generate_mnemonic
from mm_mnemonic.network import check_network_security
from mm_mnemonic.passphrase import generate_passphrase, prompt_encryption_password
from mm_mnemonic.types import Coin


class Params(BaseModel):
    generate_passphrase: bool
    passphrase: str | None
    prompt_passphrase: bool
    words: int
    coin: Coin
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

        # Passphrase options validation (mutually exclusive)
        passphrase_options = [self.generate_passphrase, self.passphrase is not None, self.prompt_passphrase]
        if sum(passphrase_options) > 1:
            raise typer.BadParameter(
                "Passphrase options are mutually exclusive: choose only one of "
                "--generate-passphrase, --passphrase, or --prompt-passphrase"
            )


def run(params: Params) -> None:
    params.validate_params()
    check_network_security(params.allow_internet_risk)

    try:
        # Generate new mnemonic
        mnemonic = generate_mnemonic(params.words)

        # Handle passphrase based on user choice
        if params.generate_passphrase:
            passphrase = generate_passphrase()
        elif params.passphrase is not None:
            passphrase = params.passphrase
        elif params.prompt_passphrase:
            passphrase = typer.prompt("Passphrase", hide_input=True, confirmation_prompt=True)
        else:
            # Default: no passphrase
            passphrase = ""  # nosec

        # Derive accounts
        derived_accounts = derive_accounts(
            coin=params.coin,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=params.derivation_path,
            limit=params.limit,
        )

        # Save to files if requested
        if params.output_dir:
            encryption_password = None
            if params.encrypt:
                encryption_password = prompt_encryption_password()
            output.store_derived_accounts(derived_accounts, params.output_dir, encryption_password)

        output.print_derived_accounts(derived_accounts, show_sensitive=True)

    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        sys.exit(1)
