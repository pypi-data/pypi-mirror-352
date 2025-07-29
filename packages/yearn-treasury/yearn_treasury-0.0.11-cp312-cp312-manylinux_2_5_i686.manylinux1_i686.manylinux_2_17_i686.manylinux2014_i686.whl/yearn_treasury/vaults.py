from typing import Dict, Final, List

from brownie import chain
from eth_typing import ChecksumAddress
from y import Contract, Events, Network

from yearn_treasury._ens import resolver, topics


if chain.id == Network.Mainnet:
    _v1_addresses_provider = Contract("0x9be19Ee7Bc4099D62737a7255f5c227fBcd6dB93")
    _addresses_generator_v1_vaults = Contract(
        _v1_addresses_provider.addressById("ADDRESSES_GENERATOR_V1_VAULTS")
    )

    v1: Dict[Contract, ChecksumAddress] = {
        vault: vault.token()  # type: ignore [misc]
        for vault in map(Contract, _addresses_generator_v1_vaults.assetsAddresses())
    }

    now = chain.height

    v2_registries = [
        Contract(event["newAddress"].hex())  # type: ignore [attr-defined]
        for event in Events(  # type: ignore [attr-defined]
            addresses=resolver, topics=topics
        ).events(now)
    ]

    v2: List[Contract] = [
        Contract(vault)
        for vault in {
            event["vault"]
            for event in Events(addresses=list(map(str, v2_registries))).events(now)
            if event.name == "NewVault"
        }
    ]

else:
    v1 = {}
    v2 = []
    raise NotImplementedError(v2)
