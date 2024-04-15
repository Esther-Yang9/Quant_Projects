import ccxt.pro as ccxtpro
import ccxt
import asyncio

import pandas as pd
import random
import numpy as np
import datetime as dt

import talib

from typing import Dict, List, Optional, Sequence, Union, cast
from abc import abstractmethod

import sys
import os



"""
ccxt pro: https://github.com/ccxt/ccxt/issues/15171

https://github.com/ccxt/ccxt/tree/master/examples/ccxt.pro/py
https://github.com/ccxt/ccxt/blob/master/examples/py/watch-OHLCV-For-Symbols.py

"""




# ABC Design Pattern
class DataStack:
    def __init__(self, length = 10):
        self.stack = []
        self.length = length

    def push(self, data):
        if len(self.stack) >= self.length:
            self.pop_oldest()
        self.stack.append(data)

    def pop(self):
        # This method removes the most recent item
        if self.stack:
            return self.stack.pop()
        else:
            print("Stack is empty")
            return None

    def pop_oldest(self):
        # This method removes the oldest item to maintain the stack's fixed size
        if self.stack:
            return self.stack.pop(0)
        else:
            print("Stack is empty")
            return None
        
    def __len__(self):
        return len(self.stack)
    
    def __getitem__(self, key):
        return self.stack[key]
    
    def __repr__(self):
        return str(self.stack)
    
    def df(self):
        return pd.DataFrame(self.stack)

class WatcherBase:
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, length = 10):
        self.exchange_pro = exchange_pro
        self.data = DataStack(length)
        
    @abstractmethod
    async def next(self):
        raise NotImplementedError
    
    async def close(self):
        await self.exchange_pro.close()
    
    
# Public Watchers
class OrderbookWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, length = 10, limit: int = 5, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.params = params
        self.limit = limit
        
    async def next(self):
        orderbook = await self.exchange_pro.watch_order_book(symbol = self.symbol, limit = self.limit, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': {'ask': orderbook['asks'][0], 'bid': orderbook['bids'][0]},
            'info': orderbook,  
        }
        self.data.push(datainfo)
        return datainfo


class TickerWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, length = 10, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.params = params
        
    async def next(self):
        ticker = await self.exchange_pro.watch_ticker(symbol = self.symbol, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': {'last': ticker['last'],'baseVolume': ticker['baseVolume'], 'quoteVolume': ticker['quoteVolume'], 'percentage': ticker['percentage']},
            'info': ticker,
        }
        
        """Sample
        ['2024-03-27T23:29:06.937Z', 'Gate.io', 'BTC/USDT:USDT', {'last': 69277.2, 'baseVolume': 19449.0, 'quoteVolume': 1347722188.0, 'percentage': -1.0993}]
        """
        self.data.push(datainfo)
        return datainfo
    
class OHLCVWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, timeframe = '1m', length = 10, since = None, limit = 5, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.timeframe = timeframe
        self.since = since
        self.limit = limit
        self.params = params
        
    async def next(self):
        ohlcv = await self.exchange_pro.watch_ohlcv(symbol = self.symbol, timeframe = self.timeframe, since = self.since, limit = self.limit, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': ohlcv[-1],
            'info': ohlcv,  
        }
        self.data.push(datainfo)
        return datainfo
    
class TradesWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, length = 10, since = None, limit = None, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.params = params
        self.since = since
        self.limit = limit
        
    async def next(self):
        trades = await self.exchange_pro.watch_trades(symbol = self.symbol, since = self.since, limit = self.limit, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': trades[-1],
            'info': trades,
        }
        self.data.push(datainfo)
        return datainfo


# Private Watchers
class BalanceWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, length = 10, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.params = params
        
    async def next(self):
        account = await self.exchange_pro.watch_balance(params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': None,
            'last': account,
            'info': account,
        }
        
        """Sample
        ['2024-03-27T23:31:46.454Z', 'Gate.io', None, {'info': [{'balance': 146.602901958999, 'change': -0.00692526, 'currency': 'usdt', 'text': 'BTC_USDT:441170955819', 'time': 1711582306, 'time_ms': 1711582306388, 'type': 'fee', 'user': '11908462'}], 'timestamp': 1711582306404, 'datetime': '2024-03-27T23:31:46.404Z', 'USDT': {'free': None, 'used': None, 'total': 146.602901958999}, 'free': {'USDT': None}, 'used': {'USDT': None}, 'total': {'USDT': 146.602901958999}}]
        ['2024-03-27T23:31:46.455Z', 'Gate.io', None, {'info': [{'balance': 146.528321958999, 'change': -0.07458, 'currency': 'usdt', 'text': 'BTC_USDT:441170955819', 'time': 1711582306, 'time_ms': 1711582306388, 'type': 'pnl', 'user': '11908462'}], 'timestamp': 1711582306404, 'datetime': '2024-03-27T23:31:46.404Z', 'USDT': {'free': None, 'used': None, 'total': 146.528321958999}, 'free': {'USDT': None}, 'used': {'USDT': None}, 'total': {'USDT': 146.528321958999}}]
        """
        
        self.data.push(datainfo)
        return datainfo
    
class OrdersWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, length = 10, since = None, limit = None, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.params = params
        self.since = since
        self.limit = limit
        
    async def next(self):
        orders = await self.exchange_pro.watch_orders(symbol = self.symbol, since = self.since, limit = self.limit, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': orders[-1],
            'info': orders,
        }
        
        
        """Sample
        ['2024-03-27T23:37:14.460Z', 'Gate.io', 'BTC/USDT:USDT', {'id': '441173355019', 'clientOrderId': 'app', 'timestamp': 1711582634378, 'datetime': '2024-03-27T23:37:14.378Z', 'lastTradeTimestamp': 1711582634000, 'status': 'open', 'symbol': 'BTC/USDT:USDT', 'type': 'limit', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': False, 'side': 'buy', 'price': 69169.5, 'stopPrice': None, 'triggerPrice': None, 'average': None, 'amount': 5.0, 'cost': 0.0, 'filled': 0.0, 'remaining': 5.0, 'fee': None, 'fees': [], 'trades': [], 'info': {'amend_text': '-', 'biz_info': '-', 'contract': 'BTC_USDT', 'create_time': 1711582634, 'create_time_ms': 1711582634378, 'fill_price': 0, 'finish_as': '_new', 'finish_time': 1711582634, 'finish_time_ms': 1711582634378, 'iceberg': 0, 'id': 441173355019, 'is_close': False, 'is_liq': False, 'is_reduce_only': False, 'left': 5, 'mkfr': 0.00015, 'price': 69169.5, 'refr': 0, 'refu': 0, 'size': 5, 'status': 'open', 'stop_loss_price': '', 'stop_profit_price': '', 'stp_act': '-', 'stp_id': '0', 'text': 'app', 'tif': 'gtc', 'tkfr': 0.0005, 'update_id': 1, 'user': '11908462'}, 'lastUpdateTimestamp': None, 'takeProfitPrice': None, 'stopLossPrice': None}]
        ['2024-03-27T23:37:15.663Z', 'Gate.io', 'BTC/USDT:USDT', {'id': '441173355019', 'clientOrderId': 'app', 'timestamp': 1711582634378, 'datetime': '2024-03-27T23:37:14.378Z', 'lastTradeTimestamp': 1711582635000, 'status': 'closed', 'symbol': 'BTC/USDT:USDT', 'type': 'limit', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': False, 'side': 'buy', 'price': 69169.5, 'stopPrice': None, 'triggerPrice': None, 'average': 69169.5, 'amount': 5.0, 'cost': 345847.5, 'filled': 5.0, 'remaining': 0.0, 'fee': None, 'fees': [], 'trades': [], 'info': {'amend_text': '-', 'biz_info': '-', 'contract': 'BTC_USDT', 'create_time': 1711582634, 'create_time_ms': 1711582634378, 'fill_price': 69169.5, 'finish_as': 'filled', 'finish_time': 1711582635, 'finish_time_ms': 1711582635606, 'iceberg': 0, 'id': 441173355019, 'is_close': False, 'is_liq': False, 'is_reduce_only': False, 'left': 0, 'mkfr': 0.00015, 'price': 69169.5, 'refr': 0, 'refu': 0, 'size': 5, 'status': 'finished', 'stop_loss_price': '', 'stop_profit_price': '', 'stp_act': '-', 'stp_id': '0', 'text': 'app', 'tif': 'gtc', 'tkfr': 0.0005, 'update_id': 2, 'user': '11908462'}, 'lastUpdateTimestamp': None, 'takeProfitPrice': None, 'stopLossPrice': None}]
        ['2024-03-27T23:37:19.810Z', 'Gate.io', 'BTC/USDT:USDT', {'id': '441173408060', 'clientOrderId': 'app', 'timestamp': 1711582639741, 'datetime': '2024-03-27T23:37:19.741Z', 'lastTradeTimestamp': 1711582639000, 'status': 'closed', 'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': 69142.4, 'stopPrice': None, 'triggerPrice': None, 'average': 69142.4, 'amount': 5.0, 'cost': 345712.0, 'filled': 5.0, 'remaining': 0.0, 'fee': None, 'fees': [], 'trades': [], 'info': {'amend_text': '-', 'biz_info': '-', 'contract': 'BTC_USDT', 'create_time': 1711582639, 'create_time_ms': 1711582639741, 'fill_price': 69142.4, 'finish_as': 'filled', 'finish_time': 1711582639, 'finish_time_ms': 1711582639741, 'iceberg': 0, 'id': 441173408060, 'is_close': False, 'is_liq': False, 'is_reduce_only': True, 'left': 0, 'mkfr': 0.00015, 'price': 0, 'refr': 0, 'refu': 0, 'size': -5, 'status': 'finished', 'stop_loss_price': '', 'stop_profit_price': '', 'stp_act': '-', 'stp_id': '0', 'text': 'app', 'tif': 'ioc', 'tkfr': 0.0005, 'update_id': 1, 'user': '11908462'}, 'lastUpdateTimestamp': None, 'takeProfitPrice': None, 'stopLossPrice': None}]
        """
        
        self.data.push(datainfo)
        return datainfo

    
class MyTradeWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, symbol: str = None, length = 10, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.params = params
        
    async def next(self):
        trades = await self.exchange_pro.watch_my_trades(symbol = self.symbol, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': trades[-1],
            'info': trades,
        }
        """Sample
        ['2024-03-27T23:34:04.004Z', 'Gate.io', 'BTC/USDT:USDT', {'info': {'amend_text': '-', 'biz_info': '-', 'contract': 'BTC_USDT', 'create_time': 1711582443, 'create_time_ms': 1711582443954, 'fee': 0.00691401, 'id': '286662469', 'order_id': '441172042161', 'point_fee': 0, 'price': '69140.1', 'role': 'taker', 'size': 2, 'text': 'app'}, 'id': '286662469', 'timestamp': 1711582443954, 'datetime': '2024-03-27T23:34:03.954Z', 'symbol': 'BTC/USDT:USDT', 'order': '441172042161', 'type': None, 'side': 'buy', 'takerOrMaker': 'taker', 'price': 69140.1, 'amount': 2.0, 'cost': 13.82802, 'fee': None, 'fees': [{'cost': '0.00691401', 'currency': 'USDT'}, {'cost': '0', 'currency': 'GatePoint'}]}]
        ['2024-03-27T23:34:18.030Z', 'Gate.io', 'BTC/USDT:USDT', {'info': {'amend_text': '-', 'biz_info': '-', 'contract': 'BTC_USDT', 'create_time': 1711582457, 'create_time_ms': 1711582457982, 'fee': 0.0069144, 'id': '286662525', 'order_id': '441172156929', 'point_fee': 0, 'price': '69144', 'role': 'taker', 'size': -2, 'text': 'app'}, 'id': '286662525', 'timestamp': 1711582457982, 'datetime': '2024-03-27T23:34:17.982Z', 'symbol': 'BTC/USDT:USDT', 'order': '441172156929', 'type': None, 'side': 'sell', 'takerOrMaker': 'taker', 'price': 69144.0, 'amount': 2.0, 'cost': 13.8288, 'fee': None, 'fees': [{'cost': '0.0069144', 'currency': 'USDT'}, {'cost': '0', 'currency': 'GatePoint'}]}]
        """

        self.data.push(datainfo)
        return datainfo
    
class PositionsWatcher(WatcherBase):
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, length = 10, symbol: str = None, since = None, limit = None, params: dict = {}):
        super().__init__(exchange_pro, length)
        self.symbol = symbol
        self.since = since
        self.limit = limit
        self.params = params
        
        
    async def next(self):
        positions = await self.exchange_pro.watch_positions(symbols = self.symbol, since = self.since, limit = self.limit, params = self.params)
        datainfo = {
            'time': self.exchange_pro.iso8601(self.exchange_pro.milliseconds()),
            'exchange': self.exchange_pro.name,
            'symbol': self.symbol,
            'last': positions,
            'info': positions,
        }
        self.data.push(datainfo)
        return datainfo

class TraderTemplate:
    def __init__(self, exchange_pro:ccxtpro.Exchange = None, exchange:ccxt.Exchange = None):
        self.exchange_pro = exchange_pro
        self.exchange = exchange
        self.data = DataStack()
        
        # Step1: load the watcher
        self.ohlcwatcher = OHLCVWatcher(self.exchange_pro, symbol = 'BTC/USDT:USDT', timeframe = '1m', length = 2, since = None, limit = 5, params = {})
        
    async def next(self):
        # TODO Define your trading strategy here
        ohlc = await self.ohlcwatcher.next()
        print(ohlc['last'])
        # Do something with the data
        self.ohlc = self.ohlcwatcher.data
        self.ohlc_df = self.ohlc.df()[['time','exchange','symbol','last']]
        self.ohlc_df['close'] = self.ohlc_df['last'].apply(lambda x: x[4])
        self.ohlc_df['EMA_5'] = talib.EMA(self.ohlc_df['close'], timeperiod = 5)
        self.ohlc_df['EMA_10'] = talib.EMA(self.ohlc_df['close'], timeperiod = 10)
        
        if self.ohlc_df['EMA_5'].iloc[-1] > self.ohlc_df['EMA_10'].iloc[-1]:
            print("Buy Signal")
            
        if self.ohlc_df['EMA_5'].iloc[-1] < self.ohlc_df['EMA_10'].iloc[-1]:
            print("Sell Signal")
    
    async def run(self):
        # while True: # TODO: Define your own condition to stop the trading
        for i in range(10):
            await self.next()
        await self.exchange_pro.close()
        

          

if __name__ == '__main__':
    
    gatepro = ccxtpro.gate({
        'newUpdates': False,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap'
        }
    }
    )
    
    tickerwatcher = TickerWatcher(gatepro, symbol = 'BTC/USDT:USDT')
    # balancewatcher = BalanceWatcher(gatepro)
    # tradewatcher = MyTradeWatcher(gatepro, symbol = 'BTC/USDT:USDT')
    # orderwatcher = OrdersWatcher(gatepro, symbol = 'BTC/USDT:USDT')
    # positionwatcher = PositionsWatcher(gatepro, symbol = ['BTC/USDT:USDT'])
    async def main():
        print("Start")
        while True:
            dd = await tickerwatcher.next()
            # dd = await balancewatcher.next()
            # dd = await tradewatcher.next()
            # dd = await orderwatcher.next()
            # dd = await positionwatcher.next()
            print([dd[key] for key in ['time','exchange','symbol','last']])
    asyncio.run(main())
    
