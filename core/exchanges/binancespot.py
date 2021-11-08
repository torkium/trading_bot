from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import HistoricalKlinesType
import requests
import pandas as pd
import time
from decimal import *
from math import *

class BinanceSpot:
    apiKey = None
    apiSecret = None
    historic = {}

    feesRate = Decimal(0.1/100)
    klines_type = HistoricalKlinesType.FUTURES

    devise_precision = None
    price_precision = None

    ORDER_STATUS_NEW = "NEW"
    ORDER_STATUS_FILLED = "FILLED"

    @staticmethod
    def getHistoric(devise, timeframe, startDate, endDate=None, renew=False):
        if BinanceSpot.devise_precision == None:
            BinanceSpot.setDevisePrecision()
        if BinanceSpot.price_precision == None:
            BinanceSpot.setPricePrecision()
        if timeframe not in BinanceSpot.historic or renew:
            #Get history from Binance
            klinesT = None
            while klinesT == None:
                try:
                    klinesT = Client().get_historical_klines(devise, BinanceSpot.getTimeframe(timeframe), startDate, endDate, klines_type=BinanceSpot.klines_type)
                except requests.exceptions.ReadTimeout:
                    time.sleep(10)
                
            for row in klinesT:
                row[1] = Decimal(row[1])
                row[2] = Decimal(row[2])
                row[3] = Decimal(row[3])
                row[4] = Decimal(row[4])
                row[5] = Decimal(row[5])
                row[7] = Decimal(row[7])
                row[9] = Decimal(row[9])
                row[10] = Decimal(row[10])
                row[11] = Decimal(row[11])
            #Set history as python DataFrame
            histo = pd.DataFrame(klinesT, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])

            #Set the date as index
            histo = histo.set_index(histo['timestamp'])
            histo.index = pd.to_datetime(histo.index, unit='ms')
            del histo['timestamp']
            BinanceSpot.historic[timeframe] = histo
        return BinanceSpot.historic[timeframe]

    @staticmethod
    def setDevisePrecision():
        BinanceSpot.devise_precision = {}

    @staticmethod
    def setPricePrecision():
        BinanceSpot.price_precision = {}

    @staticmethod
    def getTimeframe(timeframe):
        if timeframe == "1m":
            return Client.KLINE_INTERVAL_1MINUTE
        if timeframe == "5m":
            return Client.KLINE_INTERVAL_5MINUTE
        if timeframe == "15m":
            return Client.KLINE_INTERVAL_15MINUTE
        if timeframe == "30m":
            return Client.KLINE_INTERVAL_30MINUTE
        if timeframe == "1h":
            return Client.KLINE_INTERVAL_1HOUR
        if timeframe == "2h":
            return Client.KLINE_INTERVAL_2HOUR
        if timeframe == "4h":
            return Client.KLINE_INTERVAL_4HOUR
        if timeframe == "12h":
            return Client.KLINE_INTERVAL_12HOUR
        if timeframe == "1d":
            return Client.KLINE_INTERVAL_1DAY
        if timeframe == "1w":
            return Client.KLINE_INTERVAL_1WEEK
        
    @staticmethod
    def getStartHistory(timeframe, maxPeriod):
        timestamp = round(time.time())
        if timeframe == "1m":
            return (timestamp-maxPeriod*60)*1000
        if timeframe == "5m":
            return (timestamp-maxPeriod*60*5)*1000
        if timeframe == "15m":
            return (timestamp-maxPeriod*60*15)*1000
        if timeframe == "30m":
            return (timestamp-maxPeriod*60*30)*1000
        if timeframe == "1h":
            return (timestamp-maxPeriod*3600)*1000
        if timeframe == "2h":
            return (timestamp-maxPeriod*3600*2)*1000
        if timeframe == "4h":
            value = (timestamp-maxPeriod*3600*4)*1000
            return value
        if timeframe == "12h":
            return (timestamp-maxPeriod*3600*12)*1000
        if timeframe == "1d":
            return (timestamp-maxPeriod*86400)*1000
        if timeframe == "1w":
            return (timestamp-maxPeriod*86400*7)*1000

    @staticmethod
    def waitNewCandle(callback, devise, timeframe):
        # open websocket
        twm = ThreadedWebsocketManager(api_key=BinanceSpot.apiKey, api_secret=BinanceSpot.apiSecret, testnet=False)
        twm.start()
        twm.start_kline_socket(callback=callback, symbol=devise, interval=timeframe)
        twm.join()

    @staticmethod
    def isCandleClosed(msg):
        return msg['e'] == 'kline' and msg['k']['x']

    @staticmethod
    def appendNewCandle(msg, timeframe, devise, max_period):
        if msg['e'] == 'kline' and msg['s'] == devise:
            kline = {
                    'open': Decimal(msg['k']['o']),
                    'high': Decimal(msg['k']['h']),
                    'low': Decimal(msg['k']['l']),
                    'close': Decimal(msg['k']['c']),
                    'volume': Decimal(msg['k']['q']),
                    'close_time': Decimal(msg['k']['T']),
                    'quote_av': Decimal(msg['k']['q']),
                    'trades': Decimal(msg['k']['n']),
                    'tb_base_av': Decimal(msg['k']['V']),
                    'tb_quote_av': Decimal(msg['k']['Q']),
                    'ignore': Decimal(msg['k']['B'])
            }
            df = pd.DataFrame(kline, index=[msg['k']['t']])
            df.index = pd.to_datetime(df.index, unit='ms')

            if df.index[0] in BinanceSpot.historic[timeframe].index:
                BinanceSpot.historic[timeframe].loc[df.index[0]] = df.iloc[0]
            else:
                BinanceSpot.historic[timeframe] = BinanceSpot.historic[timeframe].append(df)

            BinanceSpot.historic[timeframe] = BinanceSpot.historic[timeframe].tail(max_period)

    @staticmethod
    def getPrice(timeframe, index):
        return Decimal(BinanceSpot.historic[timeframe]['close'][index])

    @staticmethod
    def getDevise(baseCurrency, tradeCurrency):
        return tradeCurrency + baseCurrency

    @staticmethod
    def getOrder(devise, orderId):
        return None
    
    @staticmethod
    def getOrderStatus(order):
        return None
    
    @staticmethod
    def getOrderQuantity(order):
        return None
    
    @staticmethod
    def getOrderPrice(order):
        return None

    @staticmethod
    def truncateDevise(n, devise):
        decimals = BinanceSpot.devise_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def truncatePrice(n, devise):
        decimals = BinanceSpot.price_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r