from logging import getLogger
from typing import Final, Optional

from async_lru import alru_cache
from dao_treasury import TreasuryTx, revenue
from eth_typing import ChecksumAddress
from y import Contract, Network

from yearn_treasury.vaults import v1, v2


logger: Final = getLogger(__name__)

fees: Final = revenue("Fees")


# v1 helpers
def _is_y3crv(tx: TreasuryTx) -> bool:
    return (
        tx.symbol == "y3Crv"
        and (from_nickname := tx.from_nickname).startswith("Contract: Strategy")
        and from_nickname.endswith("3pool")
    )


def _is_ypool(tx: TreasuryTx) -> bool:
    return (
        tx.symbol == "yyDAI+yUSDC+yUSDT+yTUSD"
        and (from_nickname := tx.from_nickname).startswith("Contract: Strategy")
        and from_nickname.endswith("ypool")
    )


@alru_cache(maxsize=1000)
async def _get_rewards(controller: Contract, block: int) -> Optional[ChecksumAddress]:
    try:
        return await controller.rewards.coroutine(block_identifier=block)  # type: ignore [no-any-return]
    except ValueError as e:
        if str(e) == "No data was returned - the call likely reverted":
            return None
        raise


@alru_cache(maxsize=None)
async def _get_controller(vault: Contract) -> Contract:
    return await Contract.coroutine(await vault.controller)  # type: ignore [return-value]


@fees("Vaults V1", Network.Mainnet)
async def is_v1_vault_fees(tx: TreasuryTx) -> bool:
    token = tx.token.address.address

    for vault, underlying in v1.items():
        # Fees from single-sided strategies are not denominated in `vault.token` but everything else is
        if token != underlying and not _is_y3crv(tx) and not _is_ypool(tx):
            continue

        controller = await _get_controller(vault)
        rewards = await _get_rewards(controller, tx.block)
        if tx.to_address != rewards:
            logger.debug(
                "to address %s doesnt match rewards address %s", tx.to_address.address, rewards
            )
            continue
        strategy: ChecksumAddress = await controller.strategies.coroutine(
            underlying, block_identifier=tx.block
        )
        if tx.from_address != strategy:
            logger.debug(
                "from address %s doesnt match strategy %s set on controller %s",
                tx.from_address.address,
                strategy,
                controller,
            )
            continue
        return True
    return False


def is_inverse_fees_from_stash_contract(tx: TreasuryTx) -> bool:
    return (
        tx.from_address == "0xE376e8e8E3B0793CD61C6F1283bA18548b726C2e"
        and tx.to_nickname == "Token: Curve stETH Pool yVault"
    )


# TODO: add Network param to SortRule
@fees("Vaults V2")
async def is_v2_vault_fees(tx: TreasuryTx) -> bool:
    for vault in v2:
        if (
            tx.from_address == vault.address
            and tx.token == vault.address
            and tx.to_address == await vault.rewards.coroutine(block_identifier=tx.block)
        ):
            return True

    if is_inverse_fees_from_stash_contract(tx):
        if tx.value_usd > 0:  # type: ignore [operator]
            tx.value_usd *= -1  # type: ignore [operator]
        return True

    return False


@fees("Vaults V3")
def is_v3_vault_fees(tx: TreasuryTx) -> bool:
    # TODO: fill me in too
    return False
