from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd
import numpy as np

class Trader:

    '''
    EVERYTHING UP TO iteration_count 
    HAS TO BE SET MANUALLY
    '''
    #list of symbols
    products = ['PEARLS', 'BANANAS']
    symbols = ['PEARLS', 'BANANAS']

    #dict holding the strategy for each symbol
    strategy = {
        'PEARLS': 'all_time_avg',
        'BANANAS': 'floating_avg'
    }

    #guessed beginning prices can be set here, this contains prices for symbols in 'SEASHELLS'
    avg_price = {
        'PEARLS': 10000,
        'BANANAS': 4900
    }

    #set window size for floating_avg for according symbols
    floating_avg_window = {
        'BANANAS': 50
    }

    #set position limits size limits
    position_limits = {
        'BANANAS': 20;
        'PEARLS': 20;
    }


    #for counting iterations
    iteration_count = 0 

    #Dictionary wo für jedes Symbol alle market trades gespeichert werden können, siehe __init__
    historical_market_trades = {}
    daily_price = {}

    def __init__(self) -> None:
        #Fügt leere Liste in für alle Symbole in die Historie ein
        for symbol in self.symbols:
            self.historical_market_trades[symbol] = []
            self.daily_price[symbol] = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}

        #to make shure orders do not get rejected because of order size
        position_if_successfull = {}
        for product in self.products:
            if product in state.position:
                position_if_successfull[product] = state.position[product]
            else:
                position_if_successfull[product] = 0
        
        for symbol in self.symbols:

            if self.strategy[symbol] == 'all_time_avg':
                orders: list[Order] = []
                if symbol in state.market_trades:
                    self.historical_market_trades[symbol].extend(state.market_trades[symbol])
                				
				#Gets price from manually set price list in beginning
                acceptable_price = self.avg_price[symbol]

                if len(self.historical_market_trades[symbol]) > 0:
                    #get prices and according position sizen from historical trades                  
                    prices = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[symbol]])    
                    w = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[symbol]])
                    #calculate weighted average and set as acceptable price
                    price_avg = np.average(a = prices, weights = w)
                    acceptable_price = price_avg
                    print(str(acceptable_price))

                #try to find sell order to buy from

                orders = self.make_trades(acceptable_price)
                
                result[symbol] = orders


            if self.strategy[symbol] == 'floating_avg':
                orders: list[Order] = []				
                if symbol in state.market_trades:
                    self.historical_market_trades[symbol].extend(state.market_trades[symbol])
                
                acceptable_price = self.avg_price[symbol]	 		 

                daily_price_avg = 0 #das ist noch sehr dummmmmmm
                if len(state.market_trades[symbol]) > 0:
                    prices = np.array([getattr(obj, 'price') for obj in state.market_trades[symbol]])    
                    w = np.array([getattr(obj, 'price') for obj in state.market_trades[symbol]])
                    daily_price_avg = np.average(a = prices, weights = w)    
                    print(daily_price_avg)
                
                self.daily_price[symbol].append(daily_price_avg)
                
                floating_avg_start = max(self.iteration_count-50, 0)

                acceptable_price = np.average(self.daily_price[symbol][floating_avg_start:self.iteration_count])
                print(acceptable_price)
                
                #get open orders   
                order_depth: OrderDepth = state.order_depths[symbol]
                #try to find sell order to buy from
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask < acceptable_price:
                        #print(str(best_ask_volume) + ",", best_ask) #falls man loggen will
                        orders.append(Order(symbol, best_ask, -best_ask_volume))

                #try to find buy order to sell to
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        #print(str(best_bid_volume) + ",", best_bid) #falls man loggen will
                        orders.append(Order(symbol, best_bid, -best_bid_volume))
                result[symbol] = orders

        self.iteration_count += 1
        print(str(self.iteration_count))
        return result

    
    def make_trades(self, acceptable_price: int, symbol: str, state: TradingState) -> List[Order]:
        orders: list[Order] = []
        
        #get open orders   
        order_depth: OrderDepth = state.order_depths[symbol].copy()
        current_position = state.position[state.listings[symbol].product]

        market_ask_prices = sorted(order_depth.sell_orders)
        for ask_price in market_ask_prices:
            ask_price_volume = order_depth.sell_orders[ask_price]
            if ask_price < acceptable_price:
                #print(str(best_ask_volume) + ",", ask_price) #falls man loggen will
                orders.append(Order(symbol, ask_price, -ask_price_volume))
            else:
                break

        #try to find buy order to sell to
        market_bid_prices = sorted(order_depth.buy_orders)
        for bid_price in market_bid_prices
            bid_price = max(order_depth.buy_orders.keys())
            bid_price_volume = order_depth.buy_orders[bid_price]
            if bid_price > acceptable_price:
                #print(str(best_bid_volume) + ",", best_bid) #falls man loggen will
                orders.append(Order(symbol, bid_price, -bid_price_volume))
            else:
                break

        return orders



   