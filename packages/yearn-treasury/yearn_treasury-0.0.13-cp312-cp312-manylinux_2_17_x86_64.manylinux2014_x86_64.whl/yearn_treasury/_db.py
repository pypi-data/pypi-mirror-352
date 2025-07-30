# mypy: disable-error-code="arg-type"
from dao_treasury.db import Address
from y import Network
from y.constants import CHAINID

from yearn_treasury import constants


def prepare_db() -> None:
    Address.set_nickname(constants.TREASURY_MULTISIG, "Yearn Treasury")

    chad = {Network.Mainnet: "y", Network.Fantom: "f"}[CHAINID]  # type: ignore [index]

    Address.set_nickname(constants.YCHAD_MULTISIG, f"Yearn {chad}Chad Multisig")
    # Address.set_nickname(constants.STRATEGIST_MULTISIG, "Yearn Strategist Multisig")

    # This wallet is an EOA that has been used to assist in bridging tokens across chains.
    Address.set_nickname("0x5FcdC32DfC361a32e9d5AB9A384b890C62D0b8AC", "Bridge Assistooor EOA")

    # TODO move this to dao-treasury
    if CHAINID in (Network.Mainnet, Network.Fantom):
        Address.set_nickname("0xD152f549545093347A162Dce210e7293f1452150", "Disperse.app")
