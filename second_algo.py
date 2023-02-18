from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd
import numpy as np

class Trader:

    '''
    EVERYTHING UP TO iteration_count 
    HAS TO BE SET MANUALLY
    '''
    #list of products
    products = ['PEARLS', 'BANANAS']

    #dict holding the strategy for each product
    strategy = {
        'PEARLS': 'all_time_avg',
        'BANANAS': 'floating_avg'
    }

    #guessed beginning prices can be set here
    avg_price = {
        'PEARLS': 10000,
        'BANANAS': 4900
    }

    #set window size for floating_avg for according products
    floating_avg_window = {
        'BANANAS': 50
    }

    #for counting iterations
    iteration_count = 0 

    #Dictionary wo für jedes Produkt alle market trades gespeichert werden können, siehe __init__
    historical_market_trades = {}
    daily_price = {}

    def __init__(self) -> None:
        #Fügt leere Liste in für alle Produkte in die Historie ein
        for product in self.products:
            self.historical_market_trades[product] = []
            self.daily_price[product] = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        
        for product in state.order_depths.keys():

            if self.strategy[product] == 'all_time_avg':
                orders: list[Order] = []
                if product in state.market_trades:
                    self.historical_market_trades[product].extend(state.market_trades[product])
                				
				#Gets price from manually set price list in beginning
                acceptable_price = self.avg_price[product]

                if len(self.historical_market_trades[product]) > 0:
                    #get prices and according position sizen from historical trades                  
                    prices = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[product]])    
                    w = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[product]])
                    #calculate weighted average and set as acceptable price
                    price_avg = np.average(a = prices, weights = w)
                    acceptable_price = price_avg
                    print(str(acceptable_price))

                #try to find sell order to buy from

                orders = self.make_trades(acceptable_price)
                
                result[product] = orders


            if self.strategy[product] == 'floating_avg':
                orders: list[Order] = []				
                if product in state.market_trades:
                    self.historical_market_trades[product].extend(state.market_trades[product])
                
                acceptable_price = self.avg_price[product]	 		 

                daily_price_avg = 0 #das ist noch sehr dummmmmmm
                if len(state.market_trades[product]) > 0:
                    prices = np.array([getattr(obj, 'price') for obj in state.market_trades[product]])    
                    w = np.array([getattr(obj, 'price') for obj in state.market_trades[product]])
                    daily_price_avg = np.average(a = prices, weights = w)    
                    print(daily_price_avg)
                
                self.daily_price[product].append(daily_price_avg)
                
                floating_avg_start = max(self.iteration_count-50, 0)

                acceptable_price = np.average(self.daily_price[product][floating_avg_start:self.iteration_count])
                print(acceptable_price)
                
                #get open orders   
                order_depth: OrderDepth = state.order_depths[product]
                #try to find sell order to buy from
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask < acceptable_price:
                        #print(str(best_ask_volume) + ",", best_ask) #falls man loggen will
                        orders.append(Order(product, best_ask, -best_ask_volume))

                #try to find buy order to sell to
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        #print(str(best_bid_volume) + ",", best_bid) #falls man loggen will
                        orders.append(Order(product, best_bid, -best_bid_volume))
                result[product] = orders

        self.iteration_count += 1
        print(str(self.iteration_count))
        return result

    
    def make_trades(self, acceptable_price: int, product: str, state: TradingState) -> List[Order]:
        orders: list[Order] = []
        
        #get open orders   
        order_depth: OrderDepth = state.order_depths[product].copy()
        
        for best_ask in order_depth.sell_orders.keys():
            #best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = order_depth.sell_orders[best_ask]
            if best_ask < acceptable_price:
                #print(str(best_ask_volume) + ",", best_ask) #falls man loggen will
                orders.append(Order(product, best_ask, -best_ask_volume))
            else:
                break

        #try to find buy order to sell to
        while len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid > acceptable_price:
                #print(str(best_bid_volume) + ",", best_bid) #falls man loggen will
                orders.append(Order(product, best_bid, -best_bid_volume))
            else:
                break

        return orders



   