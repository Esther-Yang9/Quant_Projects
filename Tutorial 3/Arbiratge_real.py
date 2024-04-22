import sys
import os

import ccxt.pro as ccxtpro
import ccxt

from pprint import pprint
import json
import pandas as pd
import time

import asyncio

# https://github.com/ccxt/ccxt/wiki/Manual#positions
    

async def single_arbitrage(symbol: str, amount: int, tolerance: float = 100):
    
    # ################################ Exchanges Initilization ################################
    # Build A exchange
    exchange_a_name = 'binance'
    exchange_a_pro = getattr(ccxtpro, exchange_a_name)({
            'enableRateLimit': True,
            # "apiKey": "YOUR_API_KEY", ## TODO 
            # "secret": "YOUR_SECRET", ## TODO
            'options' : {
            'defaultType': 'spot'
            },
    })
    await exchange_a_pro.load_markets()
    
    exchange_a = getattr(ccxt, exchange_a_name)({
            'enableRateLimit': True,
            # "apiKey": "YOUR_API_KEY" ## TODO
            # "secret": "YOUR_SECRET" ## TODO
            'options' : {
            'defaultType': 'spot'
            },
    })
    exchange_a.load_markets()

    # Build B exchange
    exchange_b_name = 'gate'
    exchange_b_pro = getattr(ccxtpro, exchange_b_name)({
        'enableRateLimit': True,
        # "apiKey": "YOUR_API_KEY", ## TODO
        # "secret": "YOUR_SECRET ", ## TODO 
        'options' : {
            'defaultType': 'spot'
            },
    })
    await exchange_b_pro.load_markets()

    
    exchange_b = getattr(ccxt, exchange_b_name)({
        'enableRateLimit': True,
        # "apiKey": "YOUR_API_KEY", ## TODO
        # "secret": "YOUR_SECRET ", ## TODO 
        'options' : {
            'defaultType': 'spot'
            },
    })
    exchange_b.load_markets()
    
    ############################## Parameters ##############################
    # Get the commission fee
    exchange_a_taker_fee = exchange_a.markets[symbol]['taker'] 
    exchange_b_taker_fee = exchange_b.markets[symbol]['taker']

    # Indictor of the running loop

    ############################# Main Loop ##############################
    while True:
        
        ############################## Orderbook ##############################
        
        try:
            a_orderbook = await exchange_a_pro.watch_order_book(symbol) # equals to `exchange_a.fetch_order_book(symbol)`
            b_orderbook = await exchange_b_pro.watch_order_book(symbol) # equals to `exchange_b.fetch_order_book(symbol)`
              
            ## Calculate spread
            arbitrage_a_b = b_orderbook['bids'][0][0] - a_orderbook['asks'][0][0]  - (b_orderbook['bids'][0][0] * exchange_b_taker_fee) + (a_orderbook['asks'][0][0] * exchange_a_taker_fee) - tolerance
            arbitrage_b_a = a_orderbook['bids'][0][0] - b_orderbook['asks'][0][0]  - (a_orderbook['bids'][0][0] * exchange_a_taker_fee) + (b_orderbook['asks'][0][0] * exchange_b_taker_fee) - tolerance
            print(f'{exchange_a.iso8601(exchange_a.milliseconds())}, symbol, {exchange_a.name} ask: {a_orderbook["asks"][0][0]}, bid: {a_orderbook["bids"][0][0]}, {exchange_b.name} ask: {b_orderbook["asks"][0][0]}, bid: {b_orderbook["bids"][0][0]}, arbitrage_a_b: {arbitrage_a_b}, arbitrage_b_a: {arbitrage_b_a}')
            
            ############################## Order ##############################
            if arbitrage_a_b > 0 or arbitrage_b_a > 0:
                if arbitrage_a_b > 0: # exchange_b_bid > exchange_a_ask. Buy in exchange_a with Ask price, Sell in exchange_b with Bid price
                    ############################ Open the position ####################################
                    print("Arbitrage opportunity found, buy in exchange_a with Ask price, sell in exchange_b with Bid price")
                    print(f'{exchange_a.name} ask: {a_orderbook["asks"][0][0]}, {exchange_b.name} bid: {b_orderbook["bids"][0][0]}')
                    # exchange_a_order = exchange_a.create_order(symbol, 'market', 'buy', exchange_a_amount, params)
                    # exchange_b_order = exchange_b.create_order(symbol, 'market', 'sell', exchange_b_amount, params)
                    print('Orders placed')
                    break

                    
                elif arbitrage_b_a > 0 : # bi_bid > exchange_b_ask. Buy in exchange_b with Ask price, Sell in exchange_a with Bid price
                    ############################ Open the position ####################################
                    print("Arbitrage opportunity found, buy in exchange_b with Ask price, sell in exchange_a with Bid price")
                    # exchange_a_order = exchange_a.create_order(symbol, 'market', 'sell', exchange_a_amount, params)
                    # exchange_b_order = exchange_b.create_order(symbol, 'market', 'buy', exchange_b_amount, params)
                    print('Orders placed')
                    break
                 
        except Exception as e:
            print(type(e).__name__, str(e))
            break
            # continue
        
    await exchange_a_pro.close()
    await exchange_b_pro.close()

if __name__ == '__main__':
    
    symbol = 'BTC/USDT'
    amount = 0.001
    tolerance = 100 # The tolerance of the arbitrage profit, which is used to avoid the arbitrage opportunity with a small profit
    asyncio.run(single_arbitrage(symbol = symbol, amount = amount, tolerance=tolerance))
    
    
    
    

    



