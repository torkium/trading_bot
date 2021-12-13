from binance.enums import HistoricalKlinesType
from binance.client import Client
from core.exchanges.binancespot import BinanceSpot
from math import *
from urllib.parse import quote
from json import dumps
from core.tools.logger import Logger
import requests
import time

class BinanceFutures(BinanceSpot):
    feesRate = float(0.04/100)
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
        print("long order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage * .955, devise)
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
        print("short order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][SHORT][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        order = None
        import binance
        while order == None:
            try:
                Logger.write("TRY[" + devise + "][SHORT][" + str(amount) + "]", Logger.LOG_TYPE_DEBUG)
                order = BinanceFutures.getClient().futures_create_order(
                    symbol=devise,
                    type=Client.FUTURE_ORDER_TYPE_MARKET,
                    side=Client.SIDE_SELL,
                    quantity=amount
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
            except binance.exceptions.BinanceException as e:
                if e.code == 2019:
                    Logger.write("Failed margin Margin is insufficient. reduce by 5% the amount", Logger.LOG_TYPE_DEBUG)
                    amount = amount * 0.95
                    time.sleep(30)
                else:
                    raise e
        return order["orderId"]

    @staticmethod
    def stopLossLongOrder(devise, amount, leverage, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        print("stop loss long order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage, devise)
        stopLoss = BinanceFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][LONGSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
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
                    reduceOnly = True,
                    # parameters from real query
                    # closePosition = True,
                    # placeType = "position",
                    # positionSide: "BOTH",
                    # # quantity: 0,
                    # side: Client.SIDE_SELL,
                    # stopPrice: stopLoss,
                    # symbol: devise,
                    # timeInForce: "GTE_GTC",
                    # type: "STOP_MARKET",
                    # workingType: "MARK_PRICE",
                )
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return order["orderId"]

    @staticmethod
    def stopLossShortOrder(devise, amount, leverage, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        print("stop loss short order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage, devise)
        stopLoss = BinanceFutures.truncatePrice(stopLoss, devise)
        Logger.write("[" + devise + "][SHORTSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
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
    def closeLongOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        print("close long order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][CLOSELONG][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
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
    def closeShortOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        print("close short order: devise: %s , amount: %s, leverage: %s, type: %s" % (devise, amount, leverage, type))
        amount = BinanceFutures.truncateDevise(amount * leverage, devise)
        Logger.write("[" + devise + "][CLOSESHORT][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
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
        print("close open position: devise: %s , orderIDs: %s" % (devise, orderIds))
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
    def closeOrder(orderId):
        response = BinanceFutures.getClient().futures_cancel_order(orderId)
        if 'orderId' in response:
            return response['orderId']
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
    def getCurrentPosition(devise):
        currentPosition = None
        while currentPosition == None:
            try:
                currentPosition = BinanceFutures.getClient().futures_position_information(symbol=devise)
                return currentPosition[0]
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return None

    def getOpenOrders(devise):
        openOrders = None
        while openOrders == None:
            try:
                openOrders = BinanceFutures.getClient().futures_get_open_orders(symbol="BTCUSDT")
                print(openOrders)
                return openOrders
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
        return None

    def getAllOrder():
        return BinanceFutures.getClient().futures_get_all_orders()


    @staticmethod
    def getOrderStatus(order):
        return order['status']

    @staticmethod
    def getOrderQuantity(order):
        return float(order['executedQty'])

    @staticmethod
    def getOrderPrice(order):
        return float(order['avgPrice'])

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