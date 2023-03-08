from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd
import numpy as np
import math

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
        'PEARLS': 'fixed_price',
        'BANANAS': 'none'
    }

    #guessed beginning prices can be set here, this contains prices for symbols in 'SEASHELLS'
    avg_price = {
        'PEARLS': 10000,
        'BANANAS': 4900
    }

    #set window size for floating_avg for according symbols
    floating_avg_window = {
        'BANANAS': 25
    }

    #set position limits size limits
    position_limits = {
        'BANANAS': 20,
        'PEARLS': 20
    }

    #for counting iterations
    iteration_count = 0 

    #Dictionarys to safe market data for different symbols
    historical_market_trades = {}
    daily_price = {}

    def __init__(self) -> None:
        #Fügt leere Liste in für alle Symbole in die Historie ein
        for symbol in self.symbols:
            self.historical_market_trades[symbol] = []
            self.daily_price[symbol] = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        
        for symbol in self.symbols:

            if self.strategy[symbol] == 'fixed_price':
                orders = self.make_trades(self.avg_price[symbol], symbol, state)

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

                #make orders acoording to price 
                orders = self.make_trades(acceptable_price, symbol, state)
                #try_orders = self.attempt_trades(acceptable_price, symbol, state, 1)
                #orders.extend(try_orders)


            if self.strategy[symbol] == 'floating_avg':
                orders: list[Order] = []				
                if symbol in state.market_trades:
                    self.historical_market_trades[symbol].extend(state.market_trades[symbol])
                
                acceptable_price = self.avg_price[symbol]	 		 

                #daily_price_avg = 0 #das ist noch sehr dummmmmmm
                if len(state.market_trades[symbol]) > 0:
                    prices = np.array([getattr(obj, 'price') for obj in state.market_trades[symbol]])    
                    w = np.array([getattr(obj, 'price') for obj in state.market_trades[symbol]])
                    daily_price_avg = np.average(a = prices, weights = w)    
                    #print(daily_price_avg)
                
                self.daily_price[symbol].append(daily_price_avg)
                
                floating_avg_start = max(self.iteration_count-50, 0)

                acceptable_price = np.average(self.daily_price[symbol][floating_avg_start:self.iteration_count])
                # print(acceptable_price) for tracking in the log
                
                orders = self.make_trades(acceptable_price, symbol, state)
                try_orders = self.attempt_trades(acceptable_price, symbol, state, 1)
                orders.extend(try_orders)


            result[symbol] = orders

        self.iteration_count += 1
        # print(str(self.iteration_count)

        return result

    
    def make_trades(self, acceptable_price: int, symbol: str, state: TradingState) -> List[Order]:
        orders: list[Order] = []
        product = symbol #placeholder because the line below gives an Argument Error. Need to find out when listings are filled and with what
        #product = state.listings[symbol].product
        #get open orders   
        order_depth: OrderDepth = state.order_depths[symbol]
        position_limit = self.position_limits[product]

        market_ask_prices = sorted(order_depth.sell_orders)

        current_position = 0
        if product in state.position:
            current_position = state.position[product]
    
        #buy (from open sell orders)
        for ask_price in market_ask_prices:
            max_buy_volume = position_limit - current_position
            ask_price_volume = order_depth.sell_orders[ask_price]
            buy_volume = min([max_buy_volume, ask_price_volume]) 
            if ask_price < acceptable_price:
                #print(str(best_ask_volume) + ",", ask_price) #in case one wants to log
                orders.append(Order(symbol, ask_price, buy_volume))
            else:
                break

        #sell (to open buy orders)
        market_bid_prices = sorted(order_depth.buy_orders)
        for bid_price in market_bid_prices:
            min_sell_volume = - current_position - position_limit
            bid_price_volume = order_depth.buy_orders[bid_price]
            sell_volume = max([min_sell_volume, bid_price_volume])
            if bid_price > acceptable_price:
                #print(str(best_bid_volume) + ",", best_bid) #in case one wants to log
                orders.append(Order(symbol, bid_price, sell_volume))
            else:
                break

        return orders

    
    def attempt_trades(self, acceptable_price: int, symbol: str, state: TradingState, spread: float) -> List[Order]:
        orders: list[Order] = []
        product = symbol #placeholder because the line below gives an Argument Error. Need to find out when listings are filled and with what
        #product = state.listings[symbol].product
        
        position_limit = self.position_limits[product]
        buy_volume = position_limit
        buy_price = acceptable_price - math.ceil(spread)
        orders.append(Order(symbol, buy_price, buy_volume))

        position_limit = self.position_limits[product]
        sell_volume = - position_limit
        sell_price = acceptable_price + math.ceil(spread)
        orders.append(Order(symbol, sell_price, sell_volume)) 
    
        return orders