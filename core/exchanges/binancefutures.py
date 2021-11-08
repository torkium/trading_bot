from binance.enums import HistoricalKlinesType
from binance.client import Client
from core.exchanges.binancespot import BinanceSpot
from decimal import *
from math import *
from urllib.parse import quote
from json import dumps
from core.tools.logger import Logger
import requests
import time

class BinanceFutures(BinanceSpot):
    feesRate = Decimal(0.04/100)
    klines_type = HistoricalKlinesType.FUTURES
    client = None

    @staticmethod
    def getHistoric(devise, timeframe, startDate, endDate=None, renew=False):
        if BinanceFutures.devise_precision == None or BinanceFutures.price_precision == None:
            BinanceFutures.setPrecision()
        return BinanceSpot.getHistoric(devise, timeframe, startDate, endDate, renew)
    
    @staticmethod
    def setPrecision():
        BinanceFutures.devise_precision = {}
        BinanceFutures.price_precision = {}
        info = Client().futures_exchange_info()
        for item in info['symbols']: 
            BinanceFutures.devise_precision[item['symbol']] = item['quantityPrecision']
            BinanceFutures.price_precision[item['symbol']] = item['pricePrecision']

    @staticmethod
    def longOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        Logger.write("[" + devise + "][LONG][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol=devise,
                    type=Client.FUTURE_ORDER_TYPE_MARKET,
                    side=Client.SIDE_BUY,
                    quantity=amount
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def shortOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        Logger.write("[" + devise + "][SHORT][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol=devise,
                    type=Client.FUTURE_ORDER_TYPE_MARKET,
                    side=Client.SIDE_SELL,
                    quantity=amount
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def stopLossLongOrder(devise, amount, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        stopLoss = BinanceFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][LONGSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol = devise,
                    side = Client.SIDE_SELL,
                    type = type,
                    timeInForce = Client.TIME_IN_FORCE_GTC,
                    quantity = amount,
                    stopPrice = stopLoss,
                    reduceOnly = True
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def stopLossShortOrder(devise, amount, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        stopLoss = BinanceFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][SHORTSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol = devise,
                    side = Client.SIDE_BUY,
                    type = type,
                    timeInForce = Client.TIME_IN_FORCE_GTC,
                    quantity = amount,
                    stopPrice = stopLoss,
                    reduceOnly = True
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def closeLongOrder(devise, amount, type=Client.FUTURE_ORDER_TYPE_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        Logger.write("[" + devise + "][CLOSELONG][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol=devise,
                    type=type,
                    side=Client.SIDE_SELL,
                    quantity=amount
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def closeShortOrder(devise, amount, type=Client.FUTURE_ORDER_TYPE_MARKET):
        amount = BinanceFutures.truncateDevise(amount, devise)
        Logger.write("[" + devise + "][CLOSESHORT][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_create_order(
                    symbol=devise,
                    type=type,
                    side=Client.SIDE_BUY,
                    quantity=amount
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def orderIsLiquidated(orderId):
        if orderId is not None:
            liquidationOrder = None
            while liquidationOrder == None:
                try:
                    liquidationOrder = BinanceFutures.getClient().futures_coin_liquidation_orders(recvWindow=50000)
                except requests.exceptions.ReadTimeout:
                    time.sleep(10)
            for order in liquidationOrder:
                if order['orderId'] == orderId:
                    return True
        return False

    @staticmethod
    def hasOpenedPositions(devise):
        positions = None
        while positions == None:
            try:
                positions = BinanceFutures.getClient().futures_position_information(recvWindow=50000)
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        for position in positions:
            amount = position["positionAmt"]
            if amount != "0" and float(position['unRealizedProfit']) != 0.00000000:  # if there is position
                if position["entryPrice"] > position["liquidationPrice"]:
                    return True

    @staticmethod
    def closeOpenedPositions(devise, ordersIds):
        if len(ordersIds) > 0:
            idsString = dumps(ordersIds).replace(" ", "")
            idsString = quote(idsString)
            cancel_orders = None
            while cancel_orders == None:
                try:
                    cancel_orders = BinanceFutures.getClient().futures_cancel_orders(
                        symbol=devise,
                        orderIdList=idsString
                    )
                    return cancel_orders
                except requests.exceptions.ReadTimeout:
                    time.sleep(10)
        return None

    @staticmethod
    def getOrder(devise, orderId):
        order = None
        while order == None:
            try:
                order = BinanceFutures.getClient().futures_get_order(
                    symbol=devise,
                    orderId=orderId
                )
                return order
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return None
    
    @staticmethod
    def getOrderStatus(order):
        return order['status']
    
    @staticmethod
    def getOrderQuantity(order):
        return Decimal(order['executedQty'])
    
    @staticmethod
    def getOrderPrice(order):
        return Decimal(order['avgPrice'])

    @staticmethod
    def isFilledOrder(order):
        return BinanceFutures.getOrderStatus(order) == BinanceFutures.ORDER_STATUS_FILLED

    @staticmethod
    def truncateDevise(n, devise):
        decimals = BinanceFutures.devise_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def truncatePrice(n, devise):
        decimals = BinanceFutures.price_precision[devise]
        r = floor(float(n)*10**decimals)/10**decimals
        return r

    @staticmethod
    def getClient():
        if BinanceFutures.client == None:
            BinanceFutures.client = Client(BinanceFutures.apiKey, BinanceFutures.apiSecret)
        return BinanceFutures.client