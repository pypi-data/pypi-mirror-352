import hashlib
import hmac

import base58
from nacl.signing import SigningKey

from mm_mnemonic.account import DerivedAccount

DEFAULT_DERIVATION_PATH = "m/44'/501'/{i}'/0'"
HARDENED_OFFSET = 0x80000000


def parse_path(path: str) -> list[int]:
    """
    Parse derivation path, e.g. "m/44'/501'/0'/0'".
    Returns list of indices, hardened if endswith "'".
    """
    path = path.removeprefix("m/")
    if not path:
        return []
    result = []
    for level in path.split("/"):
        if level.endswith("'"):
            result.append(int(level[:-1]) + HARDENED_OFFSET)
        else:
            result.append(int(level))
    return result


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    """HMAC-SHA512."""
    return hmac.new(key, data, hashlib.sha512).digest()


def slip10_derive_ed25519(seed: bytes, path: str) -> tuple[bytes, bytes]:
    """
    SLIP-0010 Ed25519 key derivation from seed and derivation path.

    Args:
        seed: BIP39 seed bytes.
        path: Derivation path, e.g. "m/44'/501'/0'/0'".

    Returns:
        Tuple (private_key, public_key), both bytes.
    """
    digest = hmac_sha512(b"ed25519 seed", seed)
    private_key = digest[:32]
    chain_code = digest[32:]
    for index in parse_path(path):
        # Only hardened child keys supported for Ed25519 (SLIP-0010)
        data = b"\x00" + private_key + index.to_bytes(4, "big")
        digest = hmac_sha512(chain_code, data)
        private_key = digest[:32]
        chain_code = digest[32:]
    signing_key = SigningKey(private_key)
    public_key = signing_key.verify_key.encode()
    return private_key, public_key


def derive_account(mnemonic: str, passphrase: str, path: str) -> DerivedAccount:
    """
    Derive Solana account from mnemonic, passphrase, and path.
    Returns DerivedAccount with Solana address (base58 pubkey), private key (base58), and path.
    """
    from mnemonic import Mnemonic  # Imported here to not add global dependency if not needed

    # Generate seed from mnemonic and passphrase (BIP39)
    seed = Mnemonic.to_seed(mnemonic, passphrase)
    priv, pub = slip10_derive_ed25519(seed, path)

    address = base58.b58encode(pub).decode()

    # Solana expects private key as 64 bytes: seed + pubkey
    secret_key_bytes = priv + pub
    private_key = base58.b58encode(secret_key_bytes).decode()

    return DerivedAccount(
        address=address,
        private=private_key,
        path=path,
    )
