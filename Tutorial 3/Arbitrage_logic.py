import ccxt
import pandas
import time

exchange_a = ccxt.binance({})
# exchange_a.set_sandbox_mode(True)

# exchange_a.apiKey = 'YOUR_API_KEY'
# exchange_a.secret  = 'YOUR_SECRET'

exchange_b = ccxt.gate({})
# exchange_b.set_sandbox_mode(True)

# exchange_b.apiKey = 'YOUR_API_KEY'
# exchange_b.secret  = 'YOUR_SECRET'

symbol = 'BTC/USDT'

while True:

    order_book_A = exchange_a.fetch_order_book(symbol)
    order_book_B = exchange_b.fetch_order_book(symbol)
    
    print(f'{exchange_a.iso8601(exchange_a.milliseconds())}, symbol, {exchange_a.name} buy: {order_book_A["bids"][0][0]}, sell: {order_book_A["asks"][0][0]}, {exchange_b.name} buy: {order_book_B["bids"][0][0]}, sell: {order_book_B["asks"][0][0]}')
              
    a_buy = order_book_A['bids'][0][0]
    b_sell = order_book_B['asks'][0][0]
    
    a_sell = order_book_A['asks'][0][0]
    b_buy = order_book_B['bids'][0][0]
    
    
    # When the buy price on exchange A is higher than the sell price on exchange B
    # we have an arbitrage opportunity
    # We can buy on exchange B and sell on exchange A
    if a_buy > b_sell:
        print('Arbitrage opportunity found')
        print(f'{exchange_a.name} buy: {a_buy}, {exchange_b.name} sell: {b_sell}')
        print(f'{exchange_a.name} sell: {a_sell}, {exchange_b.name} buy: {b_buy}')
        print('Profit: ', a_buy - b_sell)
        
        # Place orders here
        # exchange_a.create_market_buy_order('BTC/USD', 0.001)
        # exchange_b.create_market_sell_order('BTC/USD', 0.001)
        print('Orders placed')
        
    # elif b_buy > a_sell:
    # pass
    
    time.sleep(0.1) # Exchange rate limit
        
    