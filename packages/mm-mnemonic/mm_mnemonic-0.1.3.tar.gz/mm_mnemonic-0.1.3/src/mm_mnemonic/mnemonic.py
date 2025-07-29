from mnemonic import Mnemonic


def generate_mnemonic(words: int = 24) -> str:
    m = Mnemonic("english")
    return m.generate(strength=get_strength(words))


def get_seed(mnemonic: str, passphrase: str) -> bytes:
    return Mnemonic.to_seed(mnemonic, passphrase)


def is_valid_mnemonic(mnemonic: str) -> bool:
    return Mnemonic("english").check(mnemonic)


def get_strength(words: int) -> int:
    return {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[words]
