from dao_treasury import TreasuryTx, other_expense
from y import Network


other_expense("veYFI Launch", Network.Mainnet).match(
    hash="0x51202f9e8a9afa84a9a0c37831ca9a18508810175cb95ab7c52691bbe69a56d5",
    symbol="YFI",
)


@other_expense("yBudget Reward", Network.Mainnet)
def is_ybudget_reward(tx: TreasuryTx) -> bool:
    txhash = tx.hash
    return (
        # Epoch 2
        (
            tx.symbol == "YFI"
            and txhash == "0xae7d281b8a093da60d39179452d230de2f1da4355df3aea629d969782708da5d"
        )
        or txhash
        in (
            # Epoch 1
            "0xa1b242b2626def6cdbe49d92a06aad96fa018c27b48719a98530c5e5e0ac61c5",
            # Epoch 3
            "0x6ba3f2bed8b766ed2185df1a492b3ecab0251747c619a5d60e7401908120c9c8",
        )
    )
