from typing import Final

from dao_treasury import TreasuryTx, TreasuryWallet

from yearn_treasury.rules.constants import ZERO_ADDRESS
from yearn_treasury.rules.ignore.swaps import swaps


aave: Final = swaps("Aave")


@aave("Deposit")
def is_aave_deposit(tx: TreasuryTx) -> bool:
    # Atoken side

    # Underlying side
    # TODO we didnt need this historically??
    return False


@aave("Withdrawal")
async def is_aave_withdrawal(tx: TreasuryTx) -> bool:
    # Atoken side
    if (
        TreasuryWallet._get_instance(tx.from_address.address)  # type: ignore [union-attr, arg-type]
        and tx.to_address == ZERO_ADDRESS
        and "RedeemUnderlying" in tx._events
        and hasattr(tx.token.contract, "underlyingAssetAddress")
    ):
        for event in tx._events["RedeemUnderlying"]:
            if (
                tx.from_address == event["_user"]
                and await tx.token.contract.underlyingAssetAddress == event["_reserve"]
                and tx.token.scale_value(event["_amount"]) == tx.amount
            ):
                return True

    # Underlying side
    if TreasuryWallet._get_instance(tx.to_address.address) and "RedeemUnderlying" in tx._events:  # type: ignore [union-attr, arg-type]
        for event in tx._events["RedeemUnderlying"]:
            if (
                tx.token == event["_reserve"]
                and tx.to_address == event["_user"]
                and tx.token.scale_value(event["_amount"]) == tx.amount
            ):
                return True

    # TODO: If these end up becoming more frequent, figure out sorting hueristics.
    return tx.hash == "0x36ee5631859a15f57b44e41b8590023cf6f0c7b12d28ea760e9d8f8003f4fc50"
