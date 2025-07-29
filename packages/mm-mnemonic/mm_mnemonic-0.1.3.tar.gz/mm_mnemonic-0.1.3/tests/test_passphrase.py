from mm_mnemonic.passphrase import generate_passphrase


def test_generate_passphrase():
    p1 = generate_passphrase()
    p2 = generate_passphrase()
    assert len(p1) == len(p2) == 32
    assert p1 != p2
