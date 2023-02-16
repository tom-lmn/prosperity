from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd
import numpy as np

class Trader:

    number_of_trades = 50
    iteration_count = 0 #das ist 0
    pearl_trades = pd.DataFrame(columns = ['quantity','price'])
    pearl_price_avg = int
    banana_array_fifty = np.ones(number_of_trades)*5000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        
        if hasattr(state, 'market_trades'):
            if 'PEARLS' in state.market_trades:
                list_pearl_trades = state.market_trades['PEARLS']
            else:
                list_pearl_trades = [] 
            if 'BANANAS' in state.market_trades:
                list_banana_trades = state.market_trades['BANANAS']
            else:
                list_banana_trades = []
        else:
            list_pearl_trades = []
            list_banana_trades = []

        for product in state.order_depths.keys():

            if product == 'PEARLS':

                orders: list[Order] = []				
				
                acceptable_price = 10000
                
                for trade in list_pearl_trades:
                    self.pearl_trades.concat(pd.Series([trade.quantity, trade.price])) 		 
                    
                
                if not self.pearl_trades.empty:
                    pearl_price_avg = np.average(a = self.pearl_trades['price'], weights = self.pearl_trades['quantity'])
                    acceptable_price = pearl_price_avg
                   
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) > 0:

                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    if best_ask < acceptable_price:

                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                result[product] = orders


            if product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []				
				
                acceptable_price = 5000

                banana_trades = pd.DataFrame(columns = ['quantity','price'])
                
                for trade in list_banana_trades:
                    banana_trades.concat(pd.Series([trade.quantity, trade.price]))	 		 
                                   
                if not banana_trades.empty:
                    banana_price_avg = np.average(a = banana_trades['price'], weights = banana_trades['quantity'])
                    index = self.iteration_count % self.number_of_trades
                    self.banana_array_fifty[index] = banana_price_avg


                acceptable_price = np.average(self.banana_array_fifty)
                
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) > 0:

                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    if best_ask < acceptable_price:

                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                result[product] = orders


        self.iteration_count += 1
        print(str(self.iteration_count))
        return result