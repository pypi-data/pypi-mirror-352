import hashlib

import base58
import ecdsa
from ecdsa.ellipticcurve import PointJacobi
from eth_account.hdaccount import HDPath

from mm_mnemonic.account import DerivedAccount
from mm_mnemonic.mnemonic import get_seed

DEFAULT_DERIVATION_PATH = "m/44'/0'/0'/0/{i}"
DEFAULT_DERIVATION_PATH_TESTNET = "m/44'/1'/0'/0/{i}"


def derive_account(mnemonic: str, passphrase: str, path: str, testnet: bool = False) -> DerivedAccount:
    seed = get_seed(mnemonic, passphrase)
    private_key = HDPath(path).derive(seed)
    btc_key = Key(private_key, testnet)
    return DerivedAccount(address=btc_key.address(), private=btc_key.wif(), path=path)


class Key:
    def __init__(self, private_key: bytes, testnet: bool = False) -> None:
        self.private_key = private_key
        self.testnet = testnet

    def pubkey(self, compressed: bool = True) -> bytes:
        """Derives pubkey from private key"""
        pubkey_point: PointJacobi = int.from_bytes(self.private_key, byteorder="big") * ecdsa.curves.SECP256k1.generator
        return _pubkey_from_point_to_bytes(_get_x(pubkey_point), _get_y(pubkey_point), compressed)

    def address(self) -> str:
        """Derives legacy (p2pkh) address from pubkey"""
        out1 = _sha256(self.pubkey())
        out2 = _ripemd160(out1)
        # Base-58 encoding with a checksum
        version = bytes.fromhex("6f") if self.testnet else bytes.fromhex("00")
        checksum = _base58_cksum(version + out2)
        return base58.b58encode(version + out2 + checksum).decode()

    def wif(self, compressed_wif: bool = True) -> str:
        version = bytes.fromhex("ef") if self.testnet else bytes.fromhex("80")
        private_key_with_version = version + self.private_key
        if compressed_wif:
            private_key_with_version = version + self.private_key + b"\x01"
        # perform SHA-256 hash on the mainnet_private_key
        sha256 = hashlib.sha256()
        sha256.update(private_key_with_version)
        hash_bytes = sha256.digest()

        # perform SHA-256 on the previous SHA-256 hash
        sha256 = hashlib.sha256()
        sha256.update(hash_bytes)
        hash_bytes = sha256.digest()

        # create a checksum using the first 4 bytes of the previous SHA-256 hash
        # append the 4 checksum bytes to the mainnet_private_key
        checksum = hash_bytes[:4]

        hash_bytes = private_key_with_version + checksum

        # convert private_key_with_version + checksum into base58 encoded string
        return base58.b58encode(hash_bytes).decode()


def _get_x(point: PointJacobi) -> int:
    # Return point's x coordinate with type int
    # If gmpy/gmpy2 is installed, point.x() return type of mpz (see https://gmpy2.readthedocs.io/en/latest/mpz.html)
    # If gmpy/gmpy2 is not installed, point.x() return type of int
    return int(point.x())


def _get_y(point: PointJacobi) -> int:
    # Return point's y coordinate with type int
    return int(point.y())


def _pubkey_from_point_to_bytes(x: int, y: int, compressed: bool = True) -> bytes:
    """Constructs pubkey from its x y coordinates"""
    x_bytes = x.to_bytes(32, byteorder="big")
    y_bytes = y.to_bytes(32, byteorder="big")
    if compressed:
        parity = y & 1
        return (2 + parity).to_bytes(1, byteorder="big") + x_bytes
    return b"\04" + x_bytes + y_bytes


def _sha256(inputs: bytes) -> bytes:
    """Computes sha256"""
    sha = hashlib.sha256()
    sha.update(inputs)
    return sha.digest()


def _ripemd160(inputs: bytes) -> bytes:
    """Computes ripemd160"""
    rip = hashlib.new("ripemd160")
    rip.update(inputs)
    return rip.digest()


def _base58_cksum(inputs: bytes) -> bytes:
    """Computes base 58 four bytes check sum"""
    s1 = _sha256(inputs)
    s2 = _sha256(s1)
    return s2[0:4]
