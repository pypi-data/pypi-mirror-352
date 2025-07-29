from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from mm_mnemonic.cli import app
from mm_mnemonic.commands.search import Params


class TestSearchBasic:
    """Test basic search functionality."""

    def test_search_requires_addresses(self, runner: CliRunner) -> None:
        """Test that search command requires addresses or addresses-file."""
        result = runner.invoke(app, ["search"])

        assert result.exit_code == 2  # Typer validation error
        assert "No addresses to search for" in result.output

    def test_search_help(self, runner: CliRunner) -> None:
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search for specific addresses" in result.stdout
        assert "WILDCARD PATTERNS:" in result.stdout
        assert "0x1234*" in result.stdout
        assert "*abcd" in result.stdout
        assert "*1234*" in result.stdout


class TestSearchWithMnemonic:
    """Test search command with --mnemonic mode."""

    def test_search_exact_match(self, runner: CliRunner, mnemonic: str) -> None:
        """Test searching for exact address match."""
        # Known first address from test mnemonic
        target_address = "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537"

        result = runner.invoke(app, ["search", target_address, "--mnemonic", mnemonic, "--limit", "5", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Found 1 matches:" in result.stdout
        assert target_address in result.stdout
        assert "m/44'/60'/0'/0/0" in result.stdout  # Should be at index 0

    def test_search_wildcard_prefix(self, runner: CliRunner, mnemonic: str) -> None:
        """Test searching with prefix wildcard."""
        result = runner.invoke(app, ["search", "0xEd5308*", "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Found match for '0xEd5308*'" in result.stdout
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout
        assert "m/44'/60'/0'/0/0" in result.stdout

    def test_search_wildcard_suffix(self, runner: CliRunner, mnemonic: str) -> None:
        """Test searching with suffix wildcard."""
        result = runner.invoke(app, ["search", "*AD537", "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Found match for '*AD537'" in result.stdout
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout

    def test_search_wildcard_contains(self, runner: CliRunner, mnemonic: str) -> None:
        """Test searching with contains wildcard."""
        result = runner.invoke(app, ["search", "*0fd50*", "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Found match for '*0fd50*'" in result.stdout
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout

    def test_search_no_matches(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with no matches found."""
        result = runner.invoke(app, ["search", "0xnonexistent*", "--mnemonic", mnemonic, "--limit", "5", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "No matches found." in result.stdout

    def test_search_multiple_patterns(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with multiple address patterns."""
        result = runner.invoke(
            app, ["search", "0xEd5308*", "*44fC", "--mnemonic", mnemonic, "--limit", "5", "--allow-internet-risk"]
        )

        assert result.exit_code == 0
        # Should find both patterns
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout
        assert "0x85d8cd0Bf19132Dc0B2c92f80867a52BaeaB44fC" in result.stdout

    def test_search_with_passphrase(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with passphrase."""
        result = runner.invoke(
            app,
            ["search", "0x9858*", "--mnemonic", mnemonic, "--passphrase", "testpass", "--limit", "5", "--allow-internet-risk"],
        )

        assert result.exit_code == 0
        # With passphrase, addresses will be different
        assert "Search completed." in result.stdout

    def test_search_different_coins(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with different cryptocurrencies."""
        for coin in ["BTC", "ETH", "SOL", "TRX"]:
            result = runner.invoke(
                app, ["search", "*123*", "--mnemonic", mnemonic, "--coin", coin, "--limit", "3", "--allow-internet-risk"]
            )

            assert result.exit_code == 0
            assert f"Coin: {coin}" in result.stdout

    def test_search_custom_derivation_path(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with custom derivation path."""
        custom_path = "m/44'/60'/1'/0/{i}"
        result = runner.invoke(
            app,
            ["search", "0x*", "--mnemonic", mnemonic, "--derivation-path", custom_path, "--limit", "2", "--allow-internet-risk"],
        )

        assert result.exit_code == 0
        assert custom_path in result.stdout

    def test_search_invalid_mnemonic(self, runner: CliRunner) -> None:
        """Test search with invalid mnemonic."""
        result = runner.invoke(app, ["search", "0x123*", "--mnemonic", "invalid mnemonic phrase", "--allow-internet-risk"])

        assert result.exit_code == 1
        assert "Invalid mnemonic phrase" in result.stdout


class TestSearchWithFile:
    """Test search command with addresses file."""

    def test_search_from_file(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test searching addresses from file."""
        addresses_file = tmp_path / "addresses.txt"
        addresses_file.write_text("0xEd5308*\n*44fC\n# Comment line\n\n*nonexistent*")

        result = runner.invoke(
            app,
            ["search", "--addresses-file", str(addresses_file), "--mnemonic", mnemonic, "--limit", "5", "--allow-internet-risk"],
        )

        assert result.exit_code == 0
        assert "Found 2 matches:" in result.stdout
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout
        assert "0x85d8cd0Bf19132Dc0B2c92f80867a52BaeaB44fC" in result.stdout

    def test_search_file_and_args_combined(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test searching with both file and arguments."""
        addresses_file = tmp_path / "addresses.txt"
        addresses_file.write_text("0xEd5308*")

        result = runner.invoke(
            app,
            [
                "search",
                "*44fC",
                "--addresses-file",
                str(addresses_file),
                "--mnemonic",
                mnemonic,
                "--limit",
                "5",
                "--allow-internet-risk",
            ],
        )

        assert result.exit_code == 0
        # Should find patterns from both sources
        assert "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537" in result.stdout
        assert "0x85d8cd0Bf19132Dc0B2c92f80867a52BaeaB44fC" in result.stdout

    def test_search_file_not_found(self, runner: CliRunner, mnemonic: str) -> None:
        """Test search with non-existent addresses file."""
        result = runner.invoke(
            app, ["search", "--addresses-file", "/nonexistent/file.txt", "--mnemonic", mnemonic, "--allow-internet-risk"]
        )

        assert result.exit_code == 1
        assert "Addresses file not found" in result.stdout

    def test_search_empty_file(self, runner: CliRunner, mnemonic: str, tmp_path: Path) -> None:
        """Test search with empty addresses file."""
        addresses_file = tmp_path / "empty.txt"
        addresses_file.write_text("# Only comments\n\n  \n")

        result = runner.invoke(
            app, ["search", "--addresses-file", str(addresses_file), "--mnemonic", mnemonic, "--allow-internet-risk"]
        )

        assert result.exit_code == 1
        assert "No address patterns found to search for." in result.stdout


class TestSearchInteractive:
    """Test search command in interactive mode."""

    @patch("mm_mnemonic.commands.search.typer.prompt")
    def test_search_interactive_valid_mnemonic(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test interactive search with valid mnemonic."""
        test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mock_typer_prompt.side_effect = [test_mnemonic, ""]

        result = runner.invoke(app, ["search", "0x9858*", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Found match for '0x9858*'" in result.stdout

    @patch("mm_mnemonic.commands.search.typer.prompt")
    def test_search_interactive_invalid_mnemonic_retry(self, mock_typer_prompt: Mock, runner: CliRunner) -> None:
        """Test interactive search with invalid mnemonic requiring retry."""
        test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mock_typer_prompt.side_effect = ["invalid mnemonic", test_mnemonic, ""]

        result = runner.invoke(app, ["search", "0x9858*", "--limit", "1", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert "Invalid mnemonic" in result.stdout
        assert "Found match for '0x9858*'" in result.stdout


class TestSearchParams:
    """Test search Params class validation."""

    def test_params_validation_no_addresses(self) -> None:
        """Test Params validation when no addresses provided."""
        params = Params(
            coin="ETH",
            addresses=[],
            addresses_file=None,
            mnemonic=None,
            passphrase=None,
            derivation_path=None,
            limit=1000,
            allow_internet_risk=False,
        )

        with pytest.raises(Exception) as exc_info:
            params.validate_params()

        assert "No addresses to search for" in str(exc_info.value)

    def test_params_validation_with_addresses(self) -> None:
        """Test Params validation with addresses provided."""
        params = Params(
            coin="ETH",
            addresses=["0x123*"],
            addresses_file=None,
            mnemonic=None,
            passphrase=None,
            derivation_path=None,
            limit=1000,
            allow_internet_risk=False,
        )

        # Should not raise exception
        params.validate_params()

    def test_params_validation_with_file(self, tmp_path: Path) -> None:
        """Test Params validation with addresses file provided."""
        addresses_file = tmp_path / "test.txt"
        addresses_file.write_text("0x123*")

        params = Params(
            coin="ETH",
            addresses=[],
            addresses_file=addresses_file,
            mnemonic=None,
            passphrase=None,
            derivation_path=None,
            limit=1000,
            allow_internet_risk=False,
        )

        # Should not raise exception
        params.validate_params()


class TestSearchWildcardPatterns:
    """Test wildcard pattern matching specifically."""

    def test_wildcard_exact_match(self, runner: CliRunner, mnemonic: str) -> None:
        """Test exact address matching without wildcards."""
        exact_address = "0xEd5308054d1d0fd50d6340f3aF14D62DE67AD537"

        result = runner.invoke(app, ["search", exact_address, "--mnemonic", mnemonic, "--limit", "2", "--allow-internet-risk"])

        assert result.exit_code == 0
        assert exact_address in result.stdout

    def test_wildcard_case_insensitive(self, runner: CliRunner, mnemonic: str) -> None:
        """Test that wildcard matching is case insensitive."""
        result = runner.invoke(
            app,
            [
                "search",
                "0XED5308*",  # Uppercase
                "--mnemonic",
                mnemonic,
                "--limit",
                "2",
                "--allow-internet-risk",
            ],
        )

        assert result.exit_code == 0
        assert "Found match for '0XED5308*'" in result.stdout

    def test_wildcard_multiple_contains(self, runner: CliRunner, mnemonic: str) -> None:
        """Test contains pattern with multiple possibilities."""
        result = runner.invoke(
            app,
            [
                "search",
                "*8*",  # Very broad pattern
                "--mnemonic",
                mnemonic,
                "--limit",
                "3",
                "--allow-internet-risk",
            ],
        )

        assert result.exit_code == 0
        # Should find at least the first address
        assert "Found" in result.stdout
