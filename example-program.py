from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    test_int = int


    def __init__(self) -> None:
        self.test_int = 4;

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print(str(self.test_int))
        self.test_int += 1

        result = {}

        return result