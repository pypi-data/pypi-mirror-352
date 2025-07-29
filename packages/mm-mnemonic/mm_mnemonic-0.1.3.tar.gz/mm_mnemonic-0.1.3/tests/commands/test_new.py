"""Tests for new command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import tomlkit
from typer.testing import CliRunner

from mm_mnemonic.cli import app
from mm_mnemonic.commands.new import Params
from mm_mnemonic.types import Coin


class TestNewBasic:
    """Test basic new command functionality."""

    def test_new_basic(self, runner: CliRunner) -> None:
        """Test basic new wallet generation."""
        result = runner.invoke(app, ["new", "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Coin: ETH" in result.stdout
        assert "Mnemonic:" in result.stdout
        assert "Passphrase:" in result.stdout

    def test_new_deterministic_generation(self, runner: CliRunner) -> None:
        """Test that each run generates different results (not cached/deterministic)."""
        result1 = runner.invoke(app, ["new", "--limit", "1", "--allow-internet-risk"])
        result2 = runner.invoke(app, ["new", "--limit", "1", "--allow-internet-risk"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Should generate different mnemonics each time
        assert result1.stdout != result2.stdout


class TestNewPassphraseOptions:
    """Test passphrase options for new command."""

    def test_new_with_custom_passphrase(self, runner: CliRunner) -> None:
        """Test new wallet with custom passphrase."""
        result = runner.invoke(app, ["new", "--passphrase", "test123", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Passphrase: test123" in result.stdout

    def test_new_with_generated_passphrase(self, runner: CliRunner) -> None:
        """Test new wallet with generated passphrase."""
        result = runner.invoke(app, ["new", "--generate-passphrase", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Passphrase:" in result.stdout
        # Generated passphrase should not be empty
        passphrase_line = next(line for line in result.stdout.split("\n") if "Passphrase:" in line)
        passphrase = passphrase_line.split("Passphrase: ")[1].strip()
        assert len(passphrase) > 0

    @patch("mm_mnemonic.commands.new.typer.prompt")
    def test_new_with_prompted_passphrase(self, mock_prompt: Mock, runner: CliRunner) -> None:
        """Test new wallet with prompted passphrase."""
        mock_prompt.return_value = "prompted_pass"

        result = runner.invoke(app, ["new", "--prompt-passphrase", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Passphrase: prompted_pass" in result.stdout


class TestNewOptions:
    """Test various options for new command."""

    def test_new_different_word_counts(self, runner: CliRunner) -> None:
        """Test new wallet with different word counts."""
        for words in [12, 15, 21, 24]:
            result = runner.invoke(app, ["new", "--words", str(words), "--limit", "1", "--allow-internet-risk"])

            assert result.exit_code == 0
            mnemonic_line = next(line for line in result.stdout.split("\n") if "Mnemonic:" in line)
            mnemonic = mnemonic_line.split("Mnemonic: ")[1].strip()
            actual_words = len(mnemonic.split())
            assert actual_words == words

    def test_new_different_coins(self, runner: CliRunner) -> None:
        """Test new wallet with different coin types."""
        for coin in ["BTC", "ETH", "SOL", "TRX"]:
            result = runner.invoke(app, ["new", "--coin", coin, "--limit", "1", "--allow-internet-risk"])

            assert result.exit_code == 0
            assert f"Coin: {coin}" in result.stdout


class TestNewFileOutput:
    """Test file output functionality for new command."""

    def test_new_save_to_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test saving new wallet to files."""
        result = runner.invoke(app, ["new", "--output-dir", str(tmp_path), "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0

        # Check files are created
        keys_file = tmp_path / "keys.toml"
        addresses_file = tmp_path / "addresses.txt"
        assert keys_file.exists()
        assert addresses_file.exists()

        # Check file contents
        keys_data = tomlkit.loads(keys_file.read_text())
        assert keys_data["coin"] == "ETH"
        assert len(keys_data["accounts"]) == 2

        addresses = addresses_file.read_text().strip().split("\n")
        assert len(addresses) == 2

    @patch("mm_mnemonic.passphrase.typer.prompt")
    def test_new_save_encrypted(self, mock_prompt: Mock, runner: CliRunner, tmp_path: Path) -> None:
        """Test saving new wallet with encryption."""
        mock_prompt.return_value = "encryption_password"

        result = runner.invoke(app, ["new", "--output-dir", str(tmp_path), "--encrypt", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0

        # Check encrypted file exists
        encrypted_file = tmp_path / "keys.toml.enc"
        assert encrypted_file.exists()
        assert not (tmp_path / "keys.toml").exists()


class TestNewSecurity:
    """Test security functionality for new command."""

    @patch("mm_mnemonic.network.has_internet_connection")
    def test_security_check_blocks_without_flag(self, mock_internet: Mock, runner: CliRunner) -> None:
        """Test that security check blocks execution when internet is connected and flag not provided."""
        mock_internet.return_value = True

        result = runner.invoke(app, ["new", "--limit", "1"])

        assert result.exit_code == 1
        assert (
            "WARNING: Running with internet connection!" in result.stdout
            or "internet connection detected" in result.stdout.lower()
        )

    def test_security_check_allows_with_flag(self, runner: CliRunner) -> None:
        """Test that security check allows execution when --allow-internet-risk is provided."""
        result = runner.invoke(app, ["new", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Mnemonic:" in result.stdout


class TestNewValidation:
    """Test parameter validation for new command."""

    def test_new_mutually_exclusive_passphrase_options(self, runner: CliRunner) -> None:
        """Test that mutually exclusive passphrase options are rejected."""
        result = runner.invoke(app, ["new", "--generate-passphrase", "--passphrase", "test"])

        assert result.exit_code == 2
        assert "Passphrase options are mutually exclusive" in result.stdout

    def test_new_encrypt_without_output_dir(self, runner: CliRunner) -> None:
        """Test that --encrypt without --output-dir is rejected."""
        result = runner.invoke(app, ["new", "--encrypt"])

        assert result.exit_code == 2
        assert "Cannot use --encrypt without --output-dir" in result.stdout

    def test_new_invalid_word_count(self, runner: CliRunner) -> None:
        """Test that invalid word counts are rejected."""
        result = runner.invoke(app, ["new", "--words", "13"])

        assert result.exit_code == 2
        assert "Words must be one of: 12, 15, 21, 24" in result.stdout


class TestNewParams:
    """Test Params class validation."""

    def test_params_validation_encrypt_without_output_dir(self) -> None:
        """Test Params validation for encrypt without output_dir."""
        params = Params(
            generate_passphrase=False,
            passphrase=None,
            prompt_passphrase=False,
            words=24,
            coin=Coin.ETH,
            derivation_path=None,
            limit=10,
            output_dir=None,
            encrypt=True,
            allow_internet_risk=False,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()

        assert "Cannot use --encrypt without --output-dir" in str(exc_info.value)

    def test_params_validation_mutually_exclusive_passphrase(self) -> None:
        """Test Params validation for mutually exclusive passphrase options."""
        params = Params(
            generate_passphrase=True,
            passphrase="test",
            prompt_passphrase=False,
            words=24,
            coin=Coin.ETH,
            derivation_path=None,
            limit=10,
            output_dir=None,
            encrypt=False,
            allow_internet_risk=False,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()

        assert "Passphrase options are mutually exclusive" in str(exc_info.value)
