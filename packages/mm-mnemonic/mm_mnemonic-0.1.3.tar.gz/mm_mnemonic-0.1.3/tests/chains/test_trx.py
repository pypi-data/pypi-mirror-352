from mm_mnemonic.chains import trx


def test_derive_account(mnemonic, passphrase):
    acc = trx.derive_account(mnemonic, passphrase, "m/44'/195'/0'/0/0")
    assert acc.path == "m/44'/195'/0'/0/0"
    assert acc.address == "TRB9zZgSXxB1yQsqzVtkSuCP6PTptWergB"
    assert acc.private == "b8865970fbf0f9789c684d2794edaf7d388b265892e2faa0ff63d71326e0afde"

    acc = trx.derive_account(mnemonic, passphrase, "m/44'/195'/0'/0/7")
    assert acc.path == "m/44'/195'/0'/0/7"
    assert acc.address == "TDJK7kwaJkBi8kuX4rQYFa22vad9WVfbUJ"
    assert acc.private == "7e8780c8ab1eea6e5f5624ccc2bb3a533c62b49f853eeda7a75c67c9229d8492"
