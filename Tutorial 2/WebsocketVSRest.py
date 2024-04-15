import ccxt
import ccxt.pro as ccxtpro
import asyncio

# REST API


def restapi():
    exchange = ccxt.binance()
    exchange.set_sandbox_mode(True) 
    print('REST API....')

    for i in range(10):
        data = exchange.fetchOrderBook('BTC/USDT', limit=1)
        print(data)
        
    return
        
        
async def websocketapi():
    
    print('Websocket API....')
    exchange = ccxtpro.binance()
    await exchange.load_markets()
    
    for i in range(10):
        data = await exchange.watch_order_book('BTC/USDT', limit=1)
        print(data)
    
    await exchange.close()
    return

if __name__ == '__main__':
    restapi()
    asyncio.run(websocketapi())
    
    