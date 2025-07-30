from typing import Final

from dao_treasury import TreasuryTx, expense


grants: Final = expense("Grants")
website: Final = grants("Website")
ux: Final = website("UX")


@expense("Coordinape")
def is_coordinape(tx: TreasuryTx) -> bool:
    return (
        tx.from_nickname == "Disperse.app"
        and tx.symbol in ("YFI", "yvYFI")
        and tx
        in {
            "0x0b7159645e66c3b460efeb3e1e3c32d5e4eb845a2f2230b28b388ad34a36fcc3",
            "0xb23d189ac94acb68d457e5a21b765fd0affd73ac1cd5afbe9fb57db8c3f95c30",
            "0x5cf6a4c70ec2de7cd25a627213344deae28f11ba9814d5cc1b00946f356ed5bf",
            "0x2a7c60bb7dd6c15a6d0351e6a2b9f01e51fa6e7df9d1e5f02a3759640211ee56",
            "0x371b6a601da36382067a20236d41f540fc77dc793d64d24fc1bdbcd2c666db2b",
            "0x514591e6f8dcac50b6deeabce8a819540cc7caecc182c39dfb93280abb34d3d6",
            "0x8226b3705657f34216483f5091f8bd3eeea385a64b6da458eeaff78521596c28",
            "0x38201edb06e8fd3b9aa9d4142594d28cb73768770fdcb68a4da24d8cb0742cfc",
            "0x4d404a04bf46b80721f03ad6b821c6d82312c53331d8e7425fb68100116d8b98",
            "0xa3627513c8c3e838feaf9ab1076be01df11c5be5a83597626950c3ac38124bba",
            "0x0a9e0f2cadb5dc3209bad74ada2fe71f2cbc0e9e2f16a4de1a29ea663e325798",
            "0xb3aab771a5581df5b1c8e6faefedcc88d91b8820c5ae5eaf9c9283014288dda2",
            "0x1391d6de1f0b5469627da1e23ddd0f892bf7d182780bc2fb807b6bf1e2d0acf1",
            "0x8ed57eff8f4a61cd40d109223c5054f87e35a6f0a5c85b65b1a7afe5b6e308da",
            "0xa121fd9717d0fb4ac72a223db638f4e59094547ddee253e5ba011a5bb0c67126",
            "0xf401d432dcaaea39e1b593379d3d63dcdc82f5f694d83b098bb6110eaa19bbde",
        }
    )


@grants("yGift Team Grant")
def is_ygift_grant(tx: TreasuryTx) -> bool:
    """Yearn used to use yGift to send team grants but that ended up being too expensive."""
    return tx.to_nickname == "Contract: yGift" and tx.symbol == "yyDAI+yUSDC+yUSDT+yTUSD"
