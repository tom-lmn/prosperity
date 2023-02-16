from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd
import numpy as np

class Trader:

    iteration_count = 0
    pearl_trades = pd.DataFrame(columns = ['quantity','price'])
    pearl_price_avg = int

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        
        if hasattr(state, 'market_trades'):
            list_pearl_trades = state.market_trades['PEARLS']
        else:
            list_pearl_trades = []
        


        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                orders: list[Order] = []				
				
                acceptable_price = 10000
                
                for trade in list_pearl_trades:
                    self.pearl_trades.append({'quantity': trade.quantity, 'price': trade.price}, ignore_index=True)	 		 
                    
                
                if not self.pearl_trades.empty:
                    pearl_price_avg = np.average(a = self.pearl_trades['price'], weights = self.pearl_trades['quantity'])
                    # Define a fair value for the PEARLS.
                    acceptable_price = pearl_price_avg
                   
                    
                if(self.iteration_count > 50):
                
                    # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                    order_depth: OrderDepth = state.order_depths[product]

                    # Initialize the list of Orders to be sent as an empty list
                    

                    

                    # If statement checks if there are any SELL orders in the PEARLS market
                    if len(order_depth.sell_orders) > 0:

                        # Sort all the available sell orders by their price,
                        # and select only the sell order with the lowest price
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = order_depth.sell_orders[best_ask]

                        # Check if the lowest ask (sell order) is lower than the above defined fair value
                        if best_ask < acceptable_price:

                            # In case the lowest ask is lower than our fair value,
                            # This presents an opportunity for us to buy cheaply
                            # The code below therefore sends a BUY order at the price level of the ask,
                            # with the same quantity
                            # We expect this order to trade with the sell order
                            print("BUY", str(-best_ask_volume) + "x", best_ask)
                            orders.append(Order(product, best_ask, -best_ask_volume))

                    # The below code block is similar to the one above,
                    # the difference is that it find the highest bid (buy order)
                    # If the price of the order is higher than the fair value
                    # This is an opportunity to sell at a premium
                    if len(order_depth.buy_orders) != 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]
                        if best_bid > acceptable_price:
                            print("SELL", str(best_bid_volume) + "x", best_bid)
                            orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above

            if product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())

                    #bananamin = best_ask

                    #print("best ask is" + str(bananamin))

        self.iteration_count += 1
        print(str(self.iteration_count))
        return result