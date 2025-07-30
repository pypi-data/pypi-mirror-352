from typing import Final

from dao_treasury import IgnoreSortRule, SortRuleFactory, ignore


swaps: Final[SortRuleFactory[IgnoreSortRule]] = ignore("Swaps")


from yearn_treasury.rules.ignore.swaps.aave import *
from yearn_treasury.rules.ignore.swaps.compound import *
from yearn_treasury.rules.ignore.swaps.uniswap import *
