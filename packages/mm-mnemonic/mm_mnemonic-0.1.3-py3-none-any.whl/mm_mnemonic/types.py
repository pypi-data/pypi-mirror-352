from enum import StrEnum, unique


@unique
class Coin(StrEnum):
    BTC = "BTC"  # bitcoin
    BTC_TESTNET = "BTC_TESTNET"  # bitcoin testnet
    ETH = "ETH"  # ethereum
    SOL = "SOL"  # solana
    TRX = "TRX"  # tron
