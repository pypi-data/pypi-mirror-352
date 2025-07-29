from eth_account import Account

from mm_mnemonic.account import DerivedAccount

DEFAULT_DERIVATION_PATH = "m/44'/60'/0'/0/{i}"

Account.enable_unaudited_hdwallet_features()


def derive_account(mnemonic: str, passphrase: str, path: str) -> DerivedAccount:
    acc = Account.from_mnemonic(mnemonic, passphrase=passphrase, account_path=path)
    private_key = acc.key.hex()
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    return DerivedAccount(address=acc.address, private=private_key, path=path)
