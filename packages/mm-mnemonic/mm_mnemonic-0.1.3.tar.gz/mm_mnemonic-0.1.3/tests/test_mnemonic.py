from mm_mnemonic.mnemonic import generate_mnemonic, get_seed, is_valid_mnemonic


def test_generate_mnemonic():
    assert generate_mnemonic() != generate_mnemonic()
    assert len(generate_mnemonic().split()) == 24


def test_get_seed(mnemonic, passphrase, seed):
    assert get_seed(mnemonic, passphrase).hex() == seed


def test_is_is_valid_mnemonic(mnemonic):
    bad_mnemonic = "almost harsh bag amused margin alpha coffee shoot letter science twin plate move depart badge rough bacon bomb dwarf jealous mistake repeat agree crop"  # noqa: E501
    assert is_valid_mnemonic(mnemonic)
    assert not is_valid_mnemonic(bad_mnemonic)
    assert not is_valid_mnemonic("123")
    assert not is_valid_mnemonic("")
