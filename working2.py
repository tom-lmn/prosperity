from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd
import numpy as np
import math
#Working good for pinacolada: 5250.5, pearls: 702.0, berries:1232.0
class Trader:

    '''
    EVERYTHING UP TO iteration_count 
    HAS TO BE SET MANUALLY
    '''
    #list of symbols
    products = ['PEARLS', 'BANANAS', 'COCONUTS', 'PINA_COLADAS','BERRIES']
    symbols = ['PEARLS', 'BANANAS','COCONUTS', 'PINA_COLADAS','BERRIES']

    #dict holding the strategy for each symbol
    strategy = {
        'PEARLS': 'fixed_price',
        'BANANAS': 'fixed_price',
        'COCONUTS' :'fixed_price',
        'PINA_COLADAS' :'fixed_price',
        'DIVING_GEAR': 'diving',
        'BERRIES': 'fixed_price'
    }

    #guessed beginning prices can be set here, this contains prices for symbols in 'SEASHELLS'
    avg_price = {
        'PEARLS': 10000,
        'BANANAS': 4950,
        'COCONUTS' : 8000,
        'PINA_COLADAS' : 15000,
        'DIVING_GEAR': 99200,
        'BERRIES': 3970
    }

    #set window size for floating_avg for according symbols
    floating_avg_window = {
        'BANANAS': 15
    }

    #set position limits size limits
    position_limits = {
       'BANANAS': 20,
        'PEARLS': 20,
        'COCONUTS' : 600,
        'PINA_COLADAS' : 300,
        'DIVING_GEAR': 50,
        'BERRIES': 250
    }

    #for counting iterations
    iteration_count = 0 

    #Dictionarys to safe market data for different symbols
    historical_market_trades = {}
    daily_price = {}

    dolphins_last_round = 0
    dolphin_jump = False
    last_dolphin_jump: int
    buy_gear: bool

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
                result[symbol] = orders
            
            if self.strategy[symbol] == 'diving':
                orders: list[Order] = []

                dolphins = state.observations['DOLPHIN_SIGHTINGS']
                if state.timestamp >= 100:
                    if abs(dolphins - self.dolphins_last_round > 10):
                        self.dolphin_jump = True
                        self.last_dolphin_jump = state.timestamp
                        if dolphins - self.dolphins_last_round > 0:
                            self.buy_gear = True
                        else: self.buy_gear = False
                

                rounds_until_exit = 150 # for tuning
                time_until_exit = rounds_until_exit*100

                order_depth = state.order_depths[symbol]
                current_position = state.position[symbol]
                if self.dolphin_jump:
                    if state.timestamp - self.last_dolphin_jump < 1000: #right after jump is detected buy or sell (for 10 rounds)
                        if self.buy_gear:
                            if len(order_depth.sell_orders) > 0:
                                best_ask = min(order_depth.sell_orders.keys())
                                volume = self.position_limits[symbol] - current_position
                                orders.append(Order(symbol, best_ask, volume))
                                print("," + "buy," + str(volume) + ", ", best_ask)
                        else:
                            if len(order_depth.buy_orders) > 0:
                                best_bid = max(order_depth.buy_orders.keys())
                                volume = -self.position_limits[symbol] - current_position
                                orders.append(Order(symbol, best_bid, volume))
                                print("," + "sell," + str(volume) + ", ", best_bid)
                    if (state.timestamp - self.last_dolphin_jump) > time_until_exit & current_position != 0: #after time_until_exit is over, try to exit position
                        if self.buy_gear:
                            if len(order_depth.buy_orders) > 0:
                                best_bid = max(order_depth.buy_orders.keys())
                                volume = -self.position_limits[symbol] - current_position
                                orders.append(Order(symbol, best_bid, volume))
                                print("," + "sell," + str(volume) + ", ", best_bid)
                        else:
                            if len(order_depth.sell_orders) > 0:
                                best_ask = min(order_depth.sell_orders.keys())
                                volume = self.position_limits[symbol] - current_position
                                orders.append(Order(symbol, best_ask, volume))
                                print("," + "buy," + str(volume) + ", ", best_ask)
                    if state.timestamp - self.last_dolphin_jump > time_until_exit & current_position == 0: #when position is exited, return to other behavior
                        self.dolphin_jump = False

                else:   #if no jump was seen recently, go back to strategy here (fixed_price)
                    self.make_trades
                    orders = self.make_trades(self.avg_price[symbol], symbol, state)
                
                self.dolphins_last_round = dolphins
                result[symbol] = orders

            if self.strategy[symbol] == 'spread_price':
                orders: list[Order] = []
                if symbol in state.market_trades:
                    self.historical_market_trades[symbol].extend(state.market_trades[symbol])
                				
                #Gets price from manually set price list in beginning
                acceptable_price = self.avg_price[symbol]

                if False: #len(self.historical_market_trades[symbol]) > 0:
                    #get prices and according position sizen from historical trades                  
                    prices = np.array([getattr(obj, 'price') for obj in self.historical_market_trades[symbol]]) 
                    prices=prices[:5]
                    w = np.array([getattr(obj, 'quantity') for obj in self.historical_market_trades[symbol]])
                    w=w[:5]
                    #calculate weighted average and set as acceptable price
                    acceptable_price = np.average(a = prices, weights = w)
                    #order_dep: OrderDepth = state.order_depths[symbol]
                    #acceptable_price = sorted(order_dep.sell_orders)[0]
                    print(str(acceptable_price))
                    
                    
                length: int = len(self.historical_market_trades[symbol])
                start_index = max(length-21,0)
                end_index = start_index + min(21,length)
                
                recent_price_data = self.historical_market_trades[symbol][start_index:end_index]
                prices = np.array([getattr(obj, 'price') for obj in recent_price_data])
                
                if len(prices) != 0:
                    prices[0] = np.mean(prices)
                    
                    for i in range(1,len(prices)):
                        prices[i] = 2/(1+len(prices)) * (prices[i] - prices[i-1]) + prices[i-1]
                    acceptable_price = prices[-1]
                    
                else:
                    acceptable_price = self.avg_price[symbol]
                
                orders = self.make_trades(acceptable_price, symbol, state)

                #make orders acoording to price 
                #orders = self.make_trades(acceptable_price, symbol, state)
                #try_orders = self.attempt_trades(acceptable_price, symbol, state, 1)
                #orders.extend(try_orders)
        if self.strategy[symbol] == 'moving_avg':
                orders: list[Order] = []
                order_depth = state.order_depths[symbol]
                if not symbol in self.historical_orders:
                    self.historical_orders[symbol] = pd.DataFrame(columns=["price"])

                if len(order_depth.sell_orders) > 0 & len(order_depth.buy_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_bid = min(order_depth.buy_orders.keys()) 
                    average = (best_ask + best_bid / 2)
                    self.historical_orders[symbol] = self.historical_orders[symbol].append({"price":average})
                
                number_entries = min(self.moving_avg_window[symbol],len(self.historical_orders[symbol]))
                if number_entries > 0:
                    last_entries = self.historical_orders[symbol].tail(number_entries)
                    moving_average_df = last_entries.mean()
                    moving_average = moving_average_df.iloc[0]['price']
                    self.make_trades(moving_average, symbol, state)
                else: self.make_trades(self.avg_price[symbol], symbol, state)
        self.iteration_count += 1
        # print(str(self.iteration_count)

        return result

    
    def make_trades(self, acceptable_price: int,symbol: str, state: TradingState) -> List[Order]:
        orders: list[Order] = []
        product = symbol #placeholder because the line below gives an Argument Error. Need to find out when listings are filled and with what   
        #product = state.listings[symbol].product
        #get open orders   
        order_depth: OrderDepth = state.order_depths[symbol]
        position_limit = self.position_limits[product]

        current_position = 0
        if product in state.position:
            current_position = state.position[product]
        
        if symbol=='BANANAS':
            day=2
        elif symbol=='PEARLS':
            day=0
        else:
            day=0
        #buy (from open sell orders)
        market_ask_prices = sorted(order_depth.sell_orders)
        for ask_price in market_ask_prices:
            i=1
            buy_volume = position_limit - current_position
            if ask_price < acceptable_price+day:
                print("," + "buy," + str(buy_volume) + ", ", ask_price) #in case one wants to log
                if i:
                    orders.append(Order(symbol, ask_price, buy_volume/2))
                    orders.append(Order(symbol, ask_price +2, buy_volume/3))
                    #orders.append(Order(symbol, ask_price+3, buy_volume/3))
                else:
                    break
               
                 
            else:
                break

        #sell (to open buy orders)
        market_bid_prices = sorted(order_depth.buy_orders, reverse = True)
        for bid_price in market_bid_prices:
            sell_volume = - current_position - position_limit
            if bid_price > acceptable_price-day:
                print("," + "sell," + str(sell_volume) + " ,", bid_price) #in case one wants to log
                orders.append(Order(symbol, bid_price, sell_volume/2))
                orders.append(Order(symbol, bid_price-2, sell_volume/3))
                #orders.append(Order(symbol, bid_price-3, sell_volume/3))
            else:
                break

        #try to offload part of the position if no other trades can be made
        
        d = 0.40 #fraction of position that we try to unload. Should be between 0 and 1
        if len(orders) == 0 and current_position != 0:
            if current_position > 0:
                sell_volume = - math.floor(current_position*d)
                orders.append(Order(symbol, acceptable_price, sell_volume))
            if current_position < 0:
                buy_volume = - math.ceil(current_position*d)
                orders.append(Order(symbol, acceptable_price, buy_volume))
            
        return orders