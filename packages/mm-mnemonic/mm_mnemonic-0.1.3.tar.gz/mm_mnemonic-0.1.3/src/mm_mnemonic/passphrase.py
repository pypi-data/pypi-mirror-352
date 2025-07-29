import secrets
import string

import typer


def generate_passphrase(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def prompt_encryption_password() -> str:
    """
    Prompt user for encryption password with confirmation.

    Returns:
        The validated password string

    Raises:
        typer.Abort: If user cancels the operation
    """
    while True:
        password: str = typer.prompt("Enter encryption password", hide_input=True, confirmation_prompt=True, type=str)

        if not password:
            typer.echo("Password cannot be empty. Please try again.")
            continue

        return password
