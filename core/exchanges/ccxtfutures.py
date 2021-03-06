import ccxt
from decimal import *
from math import *
from urllib.parse import quote
from json import dumps
from core.tools.logger import Logger
import requests
import time

import pandas as pd

class CCXTFutures():
    apiKey = None
    apiSecret = None
    fakeMode = True
    historic = {}
    candles = {}
    mockedOrder = {}
    mockPrice = None

    feesRate = Decimal(0.04/100)
    client = None

    devise_precision = None
    price_precision = None

    ORDER_STATUS_NEW = "NEW"
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CLOSED = "closed"

    EXCHANGE_ID = None

    @staticmethod
    def getHistoric(devise, timeframe, startDate, endDate=None, renew=False, limit=400):
        if CCXTFutures.devise_precision == None or CCXTFutures.price_precision == None:
            CCXTFutures.setPrecision()
        if timeframe not in CCXTFutures.historic or renew:
            #Get history from Exchange
            candles = None
            while candles == None:
                try:
                    candles = CCXTFutures.getClient().fetch_ohlcv(devise, timeframe=CCXTFutures.getTimeframe(timeframe), since=startDate, limit=limit)
                except:
                    time.sleep(20)
                
            for row in candles:
                row[1] = Decimal(str(row[1]))
                row[2] = Decimal(str(row[2]))
                row[3] = Decimal(str(row[3]))
                row[4] = Decimal(str(row[4]))
                row[5] = Decimal(str(row[5]))
            #Set history as python DataFrame
            histo = pd.DataFrame(candles, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            #Set the date as index
            histo = histo.set_index(histo['timestamp'])
            histo.index = pd.to_datetime(histo.index, unit='ms')
            del histo['timestamp']
            CCXTFutures.historic[timeframe] = histo
        return CCXTFutures.historic[timeframe]

    def getCandleIndexFromHistory(date, history):
        previous_index = None
        for index in history.index:
            if index == date:
                return index
            if index > date:
                return previous_index
            previous_index = index
        return previous_index

    @staticmethod
    def setPrecision():
        CCXTFutures.devise_precision = {}
        CCXTFutures.price_precision = {}
        infos = CCXTFutures.getClient().load_markets()
        for item in infos:
            CCXTFutures.devise_precision[infos[item]['info']['symbol']] = float(infos[item]['info']['quantityPrecision'])
            CCXTFutures.price_precision[infos[item]['info']['symbol']] = float(infos[item]['info']['pricePrecision'])

    @staticmethod
    def longOrder(devise, amount, leverage, type="market"):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("filled")["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][LONG][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                order = CCXTFutures.getClient().create_order(devise, type, 'buy', amount, None)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def shortOrder(devise, amount, leverage, type='market'):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("filled")["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][SHORT][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                order = CCXTFutures.getClient().create_order(devise, type, 'sell', amount, None)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def stopLossLongOrder(devise, amount, leverage, stopLoss, type='stop_market'):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("open", stopLoss)["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        stopLoss = CCXTFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][LONGSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                params = {
                    'stopPrice': stopLoss
                }
                order = CCXTFutures.getClient().create_order(devise, type, "sell", amount, None, params)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def stopLossShortOrder(devise, amount, leverage, stopLoss, type='stop_market'):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("open", stopLoss)["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        stopLoss = CCXTFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][SHORTSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                params = {
                    'stopPrice': stopLoss
                }
                order = CCXTFutures.getClient().create_order(devise, type, "buy", amount, None, params)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def closeLongOrder(devise, amount, leverage, type='market'):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("filled")["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][CLOSELONG][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                order = CCXTFutures.getClient().create_order(devise, type, "sell", amount, None)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def closeShortOrder(devise, amount, leverage, type='market'):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockOrder("filled")["id"]
        amount = CCXTFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][CLOSESHORT][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        CCXTFutures.getClient().set_leverage(leverage, devise)
        order = None
        while order == None:
            try:
                order = CCXTFutures.getClient().create_order(devise, type, "buy", amount, None)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["id"]

    @staticmethod
    def orderIsLiquidated(orderId):
        return False
        if orderId is not None:
            liquidationOrder = None
            while liquidationOrder == None:
                try:
                    liquidationOrder = CCXTFutures.getClient().futures_coin_liquidation_orders(recvWindow=50000)
                except requests.exceptions.ReadTimeout:
                    time.sleep(10)
            for order in liquidationOrder:
                if order['id'] == orderId:
                    return True
        return False

    @staticmethod
    def hasOpenedPositions(devise):
        if CCXTFutures.fakeMode:
            return None
        positions = None
        while positions == None:
            try:
                positions = CCXTFutures.getClient().futures_position_information(recvWindow=50000)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        for position in positions:
            amount = position["positionAmt"]
            if amount != "0" and float(position['unRealizedProfit']) != 0.00000000:  # if there is position
                if position["entryPrice"] > position["liquidationPrice"]:
                    return True

    @staticmethod
    def closeOpenedPositions(devise, ordersIds):
        if CCXTFutures.fakeMode:
            return None
        if len(ordersIds) > 0:
            idsString = dumps(ordersIds).replace(" ", "")
            idsString = quote(idsString)
            cancel_orders = None
            for orderId in ordersIds:
                while cancel_orders == None:
                    try:
                        cancel_orders = CCXTFutures.getClient().cancel_order(orderId, devise)
                    except requests.exceptions.ReadTimeout:
                        time.sleep(10)
        return None

    @staticmethod
    def getOrder(devise, orderId):
        if CCXTFutures.fakeMode:
            return CCXTFutures.mockedOrder[orderId]
        order = None
        while order == None:
            try:
                order = CCXTFutures.getClient().fetch_order(orderId, devise)
                return order
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return None

    @staticmethod
    def getOrderStatus(order):
        return order['status']

    @staticmethod
    def getOrderQuantity(order):
        return Decimal(str(order['amount']))

    @staticmethod
    def getOrderPrice(order):
        return Decimal(str(order['price']))

    @staticmethod
    def getOrderFeeCost(order):
        if order['fee'] != None:
            return Decimal(str(order['fee']['cost']))
        return 0

    @staticmethod
    def isFilledOrder(order):
        return order['amount'] == order['filled']

    @staticmethod
    def truncateDevise(n, devise):
        decimals = CCXTFutures.devise_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def truncatePrice(n, devise):
        decimals = CCXTFutures.price_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def getClient():
        if CCXTFutures.client == None:
            exchange_class = getattr(ccxt, CCXTFutures.EXCHANGE_ID)
            CCXTFutures.client = exchange_class({
                'apiKey': CCXTFutures.apiKey,
                'secret': CCXTFutures.apiSecret,
                'timeout': 50000,
                'enableRateLimit': True
            })
            CCXTFutures.client.options = {'defaultType': 'future', 'adjustForTimeDifference': True}
        return CCXTFutures.client


    @staticmethod
    def getTimeframe(timeframe):
        if timeframe == "1m":
            return timeframe
        if timeframe == "5m":
            return timeframe
        if timeframe == "15m":
            return timeframe
        if timeframe == "30m":
            return timeframe
        if timeframe == "1h":
            return timeframe
        if timeframe == "2h":
            return timeframe
        if timeframe == "4h":
            return timeframe
        if timeframe == "12h":
            return timeframe
        if timeframe == "1d":
            return timeframe
        if timeframe == "1w":
            return timeframe
        
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
    def getMaxPeriod(timeframe, fromTimestamp, toTimestamp):
        timestamp = toTimestamp-fromTimestamp
        return CCXTFutures.getPeriod(timeframe, timestamp)
        
    @staticmethod
    def getPeriod(timeframe, seconds):
        if timeframe == "1m":
            return int(seconds/60)
        if timeframe == "5m":
            return int(seconds/(60/5))
        if timeframe == "15m":
            return int(seconds/(60/15))
        if timeframe == "30m":
            return int(seconds/(60*30))
        if timeframe == "1h":
            return int(seconds/3600)
        if timeframe == "2h":
            return int(seconds/(3600/2))
        if timeframe == "4h":
            value = int(seconds/3600/4)
            return value
        if timeframe == "12h":
            return int(seconds/(3600/12))
        if timeframe == "1d":
            return int(seconds/86400)
        if timeframe == "1w":
            return int(seconds/(86400/7))
        
    @staticmethod
    def getSeconds(timeframe, periods):
        if timeframe == "1m":
            return int(periods*60)
        if timeframe == "5m":
            return int(periods*(60*5))
        if timeframe == "15m":
            return int(periods*(60*15))
        if timeframe == "30m":
            return int(periods*(60*30))
        if timeframe == "1h":
            return int(periods*3600)
        if timeframe == "2h":
            return int(periods*(3600*2))
        if timeframe == "4h":
            value = int(periods*(3600*4))
            return value
        if timeframe == "12h":
            return int(periods*(3600*12))
        if timeframe == "1d":
            return int(periods*86400)
        if timeframe == "1w":
            return int(periods*(86400*7))

    @staticmethod
    def isCandleClosed(msg):
        return msg['e'] == 'kline' and msg['k']['x']

    @staticmethod
    def appendNewCandle(msg, timeframe, devise, max_period):
        if msg['e'] == 'kline' and msg['s'] == devise:
            kline = {
                    'open': Decimal(str(msg['k']['o'])),
                    'high': Decimal(str(msg['k']['h'])),
                    'low': Decimal(str(msg['k']['l'])),
                    'close': Decimal(str(msg['k']['c'])),
                    'volume': Decimal(str(msg['k']['q'])),
                    'close_time': Decimal(str(msg['k']['T'])),
                    'quote_av': Decimal(str(msg['k']['q'])),
                    'trades': Decimal(str(msg['k']['n'])),
                    'tb_base_av': Decimal(str(msg['k']['V'])),
                    'tb_quote_av': Decimal(str(msg['k']['Q'])),
                    'ignore': Decimal(str(msg['k']['B']))
            }
            df = pd.DataFrame(kline, index=[msg['k']['t']])
            df.index = pd.to_datetime(df.index, unit='ms')

            if df.index[0] in CCXTFutures.historic[timeframe].index:
                CCXTFutures.historic[timeframe].loc[df.index[0]] = df.iloc[0]
            else:
                CCXTFutures.historic[timeframe] = CCXTFutures.historic[timeframe].append(df)

            CCXTFutures.historic[timeframe] = CCXTFutures.historic[timeframe].tail(max_period)

    @staticmethod
    def getPrice(timeframe, index):
        return Decimal(str(CCXTFutures.historic[timeframe]['close'][index]))

    @staticmethod
    def getHigh(timeframe, index):
        return Decimal(str(CCXTFutures.historic[timeframe]['high'][index]))

    @staticmethod
    def getLow(timeframe, index):
        return Decimal(str(CCXTFutures.historic[timeframe]['low'][index]))

    @staticmethod
    def getDevise(baseCurrency, tradeCurrency):
        return tradeCurrency + baseCurrency

    @staticmethod
    def truncateDevise(n, devise):
        decimals = CCXTFutures.devise_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def truncatePrice(n, devise):
        decimals = CCXTFutures.price_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def mockOrder(status, price=None):
        if price == None:
            price = CCXTFutures.mockPrice
        key = str(len(CCXTFutures.mockedOrder)+1)
        CCXTFutures.mockedOrder[key] = {
            "id": key,
            "status": status,
            "price": price,
            "fee": {"cost":0}
        }
        return CCXTFutures.mockedOrder[key]