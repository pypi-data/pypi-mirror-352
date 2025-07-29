"""Tests for derive command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import tomlkit
from typer.testing import CliRunner

from mm_mnemonic.cli import app
from mm_mnemonic.commands.derive import Params
from mm_mnemonic.types import Coin


class TestDeriveDirect:
    """Test derive command with direct mnemonic mode."""

    def test_direct_basic(self, runner: CliRunner, mnemonic: str) -> None:
        """Test basic direct mode with known mnemonic."""
        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Coin: ETH" in result.stdout
        assert mnemonic in result.stdout
        assert "Passphrase:" in result.stdout

    def test_direct_with_passphrase(self, runner: CliRunner, mnemonic: str, passphrase: str) -> None:
        """Test direct mode with passphrase."""
        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--passphrase", passphrase, "--limit", "1", "--allow-internet-risk"]
        )

        assert result.exit_code == 0
        assert mnemonic in result.stdout
        assert passphrase in result.stdout

    def test_direct_deterministic(self, runner: CliRunner) -> None:
        """Test that same mnemonic produces same results."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result1 = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])
        result2 = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout

    def test_direct_different_coins(self, runner: CliRunner) -> None:
        """Test direct mode with different coin types."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        for coin in ["BTC", "ETH", "SOL", "TRX"]:
            result = runner.invoke(
                app, ["derive", "--mnemonic", mnemonic, "--coin", coin, "--limit", "1", "--allow-internet-risk"]
            )
            assert result.exit_code == 0
            assert f"Coin: {coin}" in result.stdout


class TestDeriveInteractive:
    """Test derive command with interactive mode."""

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_interactive_basic(self, mock_prompt: Mock, runner: CliRunner) -> None:
        """Test basic interactive mode."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mock_prompt.side_effect = [mnemonic, "test_passphrase"]

        result = runner.invoke(app, ["derive", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert mnemonic in result.stdout
        assert "test_passphrase" in result.stdout

    @patch("mm_mnemonic.commands.derive.typer.prompt")
    def test_interactive_invalid_mnemonic_retry(self, mock_prompt: Mock, runner: CliRunner) -> None:
        """Test interactive mode with invalid mnemonic retry."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mock_prompt.side_effect = ["invalid mnemonic", mnemonic, "test_pass"]

        result = runner.invoke(app, ["derive", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert mnemonic in result.stdout
        assert "invalid mnemonic" in result.stdout


class TestDeriveFileOutput:
    """Test derive command file output functionality."""

    def test_save_to_file_basic(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test saving accounts to files."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(tmp_path), "--limit", "2", "--allow-internet-risk"]
        )

        assert result.exit_code == 0

        # Check files are created
        keys_file = tmp_path / "keys.toml"
        addresses_file = tmp_path / "addresses.txt"
        assert keys_file.exists()
        assert addresses_file.exists()

        # Check file contents
        keys_data = tomlkit.loads(keys_file.read_text())
        assert keys_data["coin"] == "ETH"
        assert keys_data["mnemonic"] == mnemonic
        assert len(keys_data["accounts"]) == 2

        addresses = addresses_file.read_text().strip().split("\n")
        assert len(addresses) == 2

    def test_file_output_hides_sensitive_info(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that saving to files hides sensitive info on screen."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(tmp_path), "--limit", "1", "--allow-internet-risk"]
        )

        assert result.exit_code == 0
        # Should show word count instead of actual mnemonic
        assert "12 words (saved to file)" in result.stdout
        assert "no" in result.stdout  # passphrase status
        # Should not show private keys in output
        assert "Private Key" not in result.stdout

    @patch("mm_mnemonic.passphrase.typer.prompt")
    def test_save_encrypted(self, mock_prompt: Mock, runner: CliRunner, tmp_path: Path) -> None:
        """Test saving encrypted files."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mock_prompt.return_value = "encryption_password"

        result = runner.invoke(
            app,
            [
                "derive",
                "--mnemonic",
                mnemonic,
                "--output-dir",
                str(tmp_path),
                "--encrypt",
                "--limit",
                "1",
                "--allow-internet-risk",
            ],
        )

        assert result.exit_code == 0

        # Check encrypted file exists
        encrypted_file = tmp_path / "keys.toml.enc"
        assert encrypted_file.exists()
        assert not (tmp_path / "keys.toml").exists()


class TestDeriveValidation:
    """Test parameter validation for derive command."""

    def test_encrypt_without_output_dir(self, runner: CliRunner) -> None:
        """Test that --encrypt without --output-dir is rejected."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--encrypt"])

        assert result.exit_code == 2
        assert "Cannot use --encrypt without --output-dir" in result.stdout

    def test_invalid_mnemonic(self, runner: CliRunner) -> None:
        """Test that invalid mnemonic is rejected."""
        result = runner.invoke(app, ["derive", "--mnemonic", "invalid mnemonic", "--allow-internet-risk"])

        assert result.exit_code == 1

    def test_invalid_coin_type(self, runner: CliRunner) -> None:
        """Test that invalid coin types are rejected."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--coin", "INVALID"])

        assert result.exit_code == 2


class TestDeriveParams:
    """Test Params class validation."""

    def test_params_validation_encrypt_without_output_dir(self) -> None:
        """Test Params validation for encrypt without output_dir."""
        params = Params(
            coin=Coin.ETH,
            mnemonic="test",
            passphrase=None,
            derivation_path=None,
            limit=10,
            output_dir=None,
            encrypt=True,
            allow_internet_risk=False,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()
        assert "Cannot use --encrypt without --output-dir" in str(exc_info.value)


class TestDeriveEdgeCases:
    """Test edge cases for derive command."""

    def test_empty_output_directory_error(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test error when output directory is not empty."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        # Create a non-empty directory
        test_dir = tmp_path / "not_empty"
        test_dir.mkdir()
        (test_dir / "existing_file.txt").write_text("test")

        result = runner.invoke(app, ["derive", "--mnemonic", mnemonic, "--output-dir", str(test_dir), "--allow-internet-risk"])

        assert result.exit_code == 1
        assert "is not empty" in result.stdout

    def test_custom_derivation_path(self, runner: CliRunner) -> None:
        """Test derive with custom derivation path."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        custom_path = "m/44'/3'/0'/0/{i}"

        result = runner.invoke(
            app, ["derive", "--mnemonic", mnemonic, "--derivation-path", custom_path, "--limit", "1", "--allow-internet-risk"]
        )

        assert result.exit_code == 0
        assert custom_path in result.stdout


class TestDeriveIntegration:
    """Integration tests for derive command."""

    def test_complete_workflow_with_files(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test complete workflow: direct mode, save to files."""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

        result = runner.invoke(
            app,
            [
                "derive",
                "--mnemonic",
                mnemonic,
                "--passphrase",
                "test",
                "--coin",
                "BTC",
                "--limit",
                "3",
                "--output-dir",
                str(tmp_path),
                "--allow-internet-risk",
            ],
        )

        assert result.exit_code == 0

        # Verify files exist and contain correct data
        keys_file = tmp_path / "keys.toml"
        addresses_file = tmp_path / "addresses.txt"
        assert keys_file.exists()
        assert addresses_file.exists()

        keys_data = tomlkit.loads(keys_file.read_text())
        assert keys_data["coin"] == "BTC"
        assert keys_data["mnemonic"] == mnemonic
        assert keys_data["passphrase"] == "test"
        assert len(keys_data["accounts"]) == 3

        # Verify console output hides sensitive info
        assert "12 words (saved to file)" in result.stdout
        assert "yes (saved to file)" in result.stdout
        assert "Private Key" not in result.stdout
