from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd
import numpy as np

class Trader:

    #list of products
    products = ['PEARLS', 'BANANAS']

    #dict holding the strategy for each product
    strategy = {
        'PEARLS': 'all_time_avg',
        'BANANAS': 'floating_avg_fifty'
    }

    historical_market_trades = Dict[str, List[Trade]]

    number_of_trades = 50
    iteration_count = 0 
    pearl_trades = pd.DataFrame(columns = ['quantity','price'])
    pearl_price_avg = int
    banana_array_fifty = np.ones(number_of_trades)*4900

    def __init__(self) -> None:

        #Fügt leere Liste in für alle Produkte in die Historie ein
        for product in self.products:
            self.historical_market_trades[product] = []



    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        
        for product in state.order_depths.keys():

            if self.strategy[product] == 'all_time_avg':
                orders: list[Order] = []

                self.historical_market_trades[product].extend(state.market_trades[product])
                				
				#müssen wir noch abstrahieren
                acceptable_price = 10000
                
                if not self.pearl_trades.empty:
                    pearl_price_avg = np.average(a = self.historical_market_trades[product].price, weights = self.historical_market_trades[product].quantity)
                    acceptable_price = pearl_price_avg
                   
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) > 0:

                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    if best_ask < acceptable_price:

                        print(str(best_ask_volume) + ",", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print(str(best_bid_volume) + ",", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                result[product] = orders


            if self.strategy[product] == 'floating_avg_fifty':
                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []				
				
                acceptable_price = 4900

                banana_trades = pd.DataFrame(columns = ['quantity','price'])
                
                for trade in state.market_trades['BANANAS']:
                    banana_trades = pd.concat([banana_trades, pd.DataFrame([[trade.quantity, trade.price]], columns = ['quantity','price'])])	 		 
                                   
                if not banana_trades.empty:
                    banana_price_avg = np.average(a = banana_trades['price'], weights = banana_trades['quantity'])
                    index = self.iteration_count % self.number_of_trades
                    self.banana_array_fifty[index] = banana_price_avg
                    print(banana_price_avg)


                acceptable_price = np.average(self.banana_array_fifty)

                print(acceptable_price)
                
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) > 0:

                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    if best_ask < acceptable_price:

                        print(str(best_ask_volume) + ",", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print(str(best_bid_volume) + ",", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                result[product] = orders


        self.iteration_count += 1
        print(str(self.iteration_count))
        return result



   