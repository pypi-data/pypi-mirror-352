from mm_mnemonic.chains import eth


def test_derive_account(mnemonic, passphrase):
    acc = eth.derive_account(mnemonic, passphrase, "m/44'/60'/0'/0/0")
    assert acc.path == "m/44'/60'/0'/0/0"
    assert acc.address == "0x06E1Aa24f223Cad92D71F31fcf5738Fd2683Ac67"
    assert acc.private == "0xcbaf62744632d6ad07e164a6437322e94edea07458b4126e937fca1225c05447"

    acc = eth.derive_account(mnemonic, passphrase, "m/44'/60'/0'/0/7")
    assert acc.path == "m/44'/60'/0'/0/7"
    assert acc.address == "0xEac0968e36946C6E3FE8F70194DD29d26106aAc5"
    assert acc.private == "0x99ff0d51ff740f42439082102236a42b2e9f0416b6fc3f238127a77bf2557e53"
