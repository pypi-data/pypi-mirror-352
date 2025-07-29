import secrets
import string
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mnemonic() -> str:
    return "label swarm identify ginger possible mistake ordinary paddle tragic day oven urge subject note tenant spin gift minute country sign very allow beyond nut"  # noqa: E501


@pytest.fixture
def passphrase() -> str:
    return "-UmMg1ce|8R6nTS~5b(ZA-''3OT{=?IB"


@pytest.fixture
def seed() -> str:
    return "3e27ae260f781346f4a747634dc8d78081ecd64a6b2dc9181a13726fd9643d30faec843fedc49df02c4f869881fadec150b156d67d092e5cf3b9972905407478"  # noqa: E501


def create_random_output_dir() -> Path:
    rnd = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    output_dir = Path(f"/tmp/mm_mnemonic_random_output_dir_{rnd}")
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir
