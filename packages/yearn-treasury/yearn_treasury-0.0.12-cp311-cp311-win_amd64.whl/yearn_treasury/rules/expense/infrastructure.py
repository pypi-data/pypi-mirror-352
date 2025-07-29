from typing import Final

from dao_treasury import expense


infrastructure: Final = expense("Infrastructure")


infrastructure("Tenderly Subscription").match(
    symbol="USDT",
    to_address="0xF6060cE3fC3df2640F72E42441355f50F195D96a",
)


infrastructure("Wonderland Jobs").match(
    symbol="DAI", to_address="0x8bA72884984f669aBBc9a5a7b441AD8E3D9a4fD3"
)
