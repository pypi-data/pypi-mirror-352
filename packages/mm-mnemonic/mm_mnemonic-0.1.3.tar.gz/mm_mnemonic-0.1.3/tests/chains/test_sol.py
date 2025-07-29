from mm_mnemonic.chains import sol


def test_derive_account(mnemonic, passphrase):
    acc = sol.derive_account(mnemonic, passphrase, "m/44'/501'/0'/0'")
    assert acc.path == "m/44'/501'/0'/0'"
    assert acc.address == "Cdt6ptYCjcwEtnpwLBMNkbEENJLNJrowiTtpTxENUxXc"
    assert acc.private == "XnmWS6UKNmdonZiciw7yu6URAGXprFD18fQcMDXw1EwnYpiQzpfE2UfJboeokMqqDE7R5nZ1LKPTCEe8ZZ8CeFC"

    acc = sol.derive_account(mnemonic, passphrase, "m/44'/501'/7'/0'")
    assert acc.path == "m/44'/501'/7'/0'"
    assert acc.address == "TiAAxKvPDVuyu8PKYTKMJpBYBRTL5Vd3n7DgW4nNAvY"
    assert acc.private == "2AKW3YGUpP9dXiTcSEuLBw1xiWF2MT6qbZUKbh3SQq3jbaZ1HNxogFTdTE8YeyvJBSCdYajxzdXjdzASbvfTeJZJ"
