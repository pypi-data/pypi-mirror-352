import base58
import eth_utils
from eth_account import Account
from eth_account.signers.local import LocalAccount

from mm_mnemonic.account import DerivedAccount

Account.enable_unaudited_hdwallet_features()

DEFAULT_DERIVATION_PATH = "m/44'/195'/0'/0/{i}"


def pubkey_to_tron_address(pubkey_bytes: bytes) -> str:
    """
    Convert an uncompressed ECDSA secp256k1 public key to a Tron base58check address.

    Args:
        pubkey_bytes: 65 bytes uncompressed SEC1 public key (starts with 0x04).

    Returns:
        Tron address (Base58Check string, starts with T).

    Raises:
        ValueError: If pubkey_bytes is not in uncompressed format.
    """
    if len(pubkey_bytes) != 65 or pubkey_bytes[0] != 0x04:
        raise ValueError("pubkey_bytes must be uncompressed SEC1 public key (65 bytes, starts with 0x04)")
    pubkey_body = pubkey_bytes[1:]  # Remove 0x04 prefix.
    digest = eth_utils.keccak(pubkey_body)[-20:]
    tron_address_bytes = b"\x41" + digest
    return base58.b58encode_check(tron_address_bytes).decode()


def derive_account(mnemonic: str, passphrase: str, path: str) -> DerivedAccount:
    acc: LocalAccount = Account.from_mnemonic(mnemonic, passphrase=passphrase, account_path=path)
    pubkey_bytes = b"\x04" + acc._key_obj.public_key.to_bytes()  # noqa: SLF001
    priv_key_hex = acc.key.hex()
    address = pubkey_to_tron_address(pubkey_bytes)
    return DerivedAccount(address=address, private=priv_key_hex, path=path)
