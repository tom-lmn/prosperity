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

    #guessed beginning prices can be set here
    avg_price = {
        'PEARLS': 10000,
        'BANANAS': 4900
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
                				
				#Gets price from manually set price list in beginning
                acceptable_price = self.avg_price[product]
                '''
                if len(self.historical_market_trades[product]) > 0:
                    #get prices and according position sizen from historical trades                  
                    prices = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[product]])    
                    w = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[product]])
                    #calculate weighted average and set as acceptable price
                    price_avg = np.average(a = prices, weights = w)
                    acceptable_price = price_avg
                    print(str(acceptable_price))

                #get open orders   
                order_depth: OrderDepth = state.order_depths[product]

                #try to find sell order to buy from
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask < acceptable_price:
                        print(str(best_ask_volume) + ",", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                #try to find buy order to sell to
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print(str(best_bid_volume) + ",", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))
`               '''
                result[product] = orders

            '''
            if self.strategy[product] == 'floating_avg_fifty':
                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []				
				
                acceptable_price = self.avg_price[product]

                banana_trades = pd.DataFrame(columns = ['quantity','price'])
                
                for trade in state.market_trades[product]:
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
            '''

        self.iteration_count += 1
        print(str(self.iteration_count))
        return result



   