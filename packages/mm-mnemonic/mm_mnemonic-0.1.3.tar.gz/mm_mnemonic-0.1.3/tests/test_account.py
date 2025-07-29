from mm_mnemonic.account import is_address_matched


def test_is_address_matched() -> None:
    """Test basic address matching functionality."""
    # Exact match
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7")

    # Prefix wildcard
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616*")
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616*")

    # Suffix wildcard
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*EBe49beC8B7A7")
    assert not is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*different")

    # Contains wildcard (new functionality)
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*D5F836*")
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*8ac27A4e4*")
    assert not is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*notfound*")

    # Prefix + suffix wildcard (middle wildcard)
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F83*dEBe49beC8B7A7")
    assert not is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F82*dEBe49beC8B7A7")

    # Edge cases
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7")
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", None)
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "")


def test_is_address_matched_case_insensitive() -> None:
    """Test that address matching is case insensitive."""
    address = "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7"

    # Case variations
    assert is_address_matched(address, "0X35B94EF616*")  # Uppercase
    assert is_address_matched(address, "0x35b94ef616*")  # Lowercase
    assert is_address_matched(address, "*bec8b7a7")  # Lowercase suffix
    assert is_address_matched(address, "*BEC8B7A7")  # Uppercase suffix
    assert is_address_matched(address, "*D5f836*")  # Mixed case contains


def test_is_address_matched_wildcard_edge_cases() -> None:
    """Test edge cases for wildcard patterns."""
    address = "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7"

    # Empty contains pattern
    assert is_address_matched(address, "**")  # Should match anything

    # Just wildcards
    assert is_address_matched(address, "*")  # Should match anything

    # Multiple contains patterns (not supported, should return False)
    assert not is_address_matched(address, "*test*middle*end*")  # Multiple * not supported
