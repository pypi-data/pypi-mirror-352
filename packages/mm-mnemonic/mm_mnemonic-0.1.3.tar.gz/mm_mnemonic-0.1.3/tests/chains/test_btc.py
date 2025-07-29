from mm_mnemonic.chains import btc


def test_derive_account(mnemonic, passphrase):
    acc = btc.derive_account(mnemonic, passphrase, "m/44'/0'/0'/0/0")
    assert acc.path == "m/44'/0'/0'/0/0"
    assert acc.address == "1DwWN2TG7XaZSR5w24dXUCugT7hGz37bWB"
    assert acc.private == "L15CKRfQT2etqYrvp4PYBmhtNzhrQUyJGTk6dLtWuNMGvFzhgxVx"

    acc = btc.derive_account(mnemonic, passphrase, "m/44'/0'/0'/0/7")
    assert acc.path == "m/44'/0'/0'/0/7"
    assert acc.address == "16G5g6WAzWZ2NiQNpo6yWiD7fgub8BctgR"
    assert acc.private == "L2AkkNRmLekKJawtDWXogV3WCXEvxmNBnj53LmTtSN9yaoGrVv3Z"
