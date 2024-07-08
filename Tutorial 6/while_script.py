import time
import ccxt 
import random


exchange = ccxt.binance({})
exchange.set_sandbox_mode(True) 
exchange.load_markets()
exchange.verbose = False

while True:
    data = exchange.fetchOrderBook('ETH/USDT', limit=1)
    print(data)
    print('-----------------------------------')
    print('Strategy:', random.choice(['Buy', 'Sell']))
    time.sleep(1)
    
    
    
