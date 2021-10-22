from binance.enums import HistoricalKlinesType
from binance.client import Client
from core.exchanges.binancespot import BinanceSpot
from decimal import *
from urllib.parse import quote
from json import dumps
from core.tools.logger import Logger

class BinanceFutures(BinanceSpot):
    feesRate = Decimal(0.04/100)
    klines_type = HistoricalKlinesType.FUTURES
    client = None

    def longOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        Logger.write("[" + devise + "][LONG][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return {
            'workingType':'CONTRACT_PRICE',
            'priceProtect':False,
            'origType':'MARKET',
            'stopPrice':'0',
            'positionSide':'BOTH',
            'side':'BUY',
            'closePosition':False,
            'reduceOnly':False,
            'type':'MARKET',
            'timeInForce':'GTC',
            'cumQuote':'0',
            'cumQty':'0',
            'executedQty':'0',
            'origQty':'0.001',
            'avgPrice':'0.00000',
            'price':'0',
            'clientOrderId':'OzWTSG8DnlKO5aRuDsuMz6',
            'status':'NEW',
            'symbol':'BTCUSDT',
            'orderId':33502125493
        }
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        longOrder = BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=Client.FUTURE_ORDER_TYPE_MARKET,
            side=Client.SIDE_BUY,
            quantity=amount
        )
        return longOrder

    def shortOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        Logger.write("[" + devise + "][SHORT][" + str(leverage) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return {
            'workingType':'CONTRACT_PRICE',
            'priceProtect':False,
            'origType':'MARKET',
            'stopPrice':'0',
            'positionSide':'BOTH',
            'side':'SELL',
            'closePosition':False,
            'reduceOnly':False,
            'type':'MARKET',
            'timeInForce':'GTC',
            'cumQuote':'0',
            'cumQty':'0',
            'executedQty':'0',
            'origQty':'0.001',
            'avgPrice':'0.00000',
            'price':'0',
            'clientOrderId':'OzWTSG8DnlKO5aRuDsuMz6',
            'status':'NEW',
            'symbol':'BTCUSDT',
            'orderId':33502125494
        }
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        shortOrder = BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=Client.FUTURE_ORDER_TYPE_MARKET,
            side=Client.SIDE_SELL,
            quantity=amount
        )
        return shortOrder

    def stopLossLongOrder(devise, amount, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        Logger.write("[" + devise + "][LONGSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return {
            'status':'NEW',
            'symbol':'BTCUSDT',
            'orderId':33501890429,
            'clientOrderId':'9tXhkQnljb4cA3Ri9iQbzw',
            'price':'0',
            'avgPrice':'0.00000',
            'origQty':'0.001',
            'executedQty':'0',
            'cumQty':'0',
            'cumQuote':'0',
            'timeInForce':'GTC',
            'type':'STOP_MARKET',
            'reduceOnly':False,
            'closePosition':False,
            'side':'SELL',
            'positionSide':'BOTH',
            'stopPrice':'53000',
            'workingType':'CONTRACT_PRICE',
            'priceProtect':False,
            'origType':'STOP_MARKET',
            'updateTime':1634043139579
        }
        return BinanceFutures.getClient().futures_create_order(
            symbol = devise, 
            side = Client.SIDE_SELL, 
            type = type, 
            timeInForce = Client.TIME_IN_FORCE_GTC, 
            quantity = amount,
            stopPrice = stopLoss
        )

    def stopLossShortOrder(devise, amount, stopLoss, type=Client.FUTURE_ORDER_TYPE_STOP_MARKET):
        Logger.write("[" + devise + "][SHORTSTOPLOSS][" + str(stopLoss) + "][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return {
            'status':'NEW',
            'symbol':'BTCUSDT',
            'orderId':33501890429,
            'clientOrderId':'9tXhkQnljb4cA3Ri9iQbzw',
            'price':'0',
            'avgPrice':'0.00000',
            'origQty':'0.001',
            'executedQty':'0',
            'cumQty':'0',
            'cumQuote':'0',
            'timeInForce':'GTC',
            'type':'STOP_MARKET',
            'reduceOnly':False,
            'closePosition':False,
            'side':'SELL',
            'positionSide':'BOTH',
            'stopPrice':'53000',
            'workingType':'CONTRACT_PRICE',
            'priceProtect':False,
            'origType':'STOP_MARKET',
            'updateTime':1634043139580
        }
        return BinanceFutures.getClient().futures_create_order(
            symbol = devise, 
            side = Client.SIDE_BUY, 
            type = type, 
            timeInForce = Client.TIME_IN_FORCE_GTC, 
            quantity = amount,
            stopPrice = stopLoss
        )

    def closeLongOrder(devise, amount, type=Client.FUTURE_ORDER_TYPE_MARKET):
        Logger.write("[" + devise + "][CLOSELONG][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return None
        return BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=type,
            side=Client.SIDE_SELL,
            quantity=amount
        )

    def closeShortOrder(devise, amount, type=Client.FUTURE_ORDER_TYPE_MARKET):
        Logger.write("[" + devise + "][CLOSESHORT][" + str(amount) + "]", Logger.LOG_TYPE_INFO)
        return None
        return BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=type,
            side=Client.SIDE_BUY,
            quantity=amount
        )
    

    def orderIsLiquidated(orderId):
        return None

    def hasOpenedPositions(devise):
        positions = BinanceFutures.getClient().futures_position_information(recvWindow=50000)
        for position in positions:
            amount = position["positionAmt"]
            if amount != "0" and float(position['unRealizedProfit']) != 0.00000000:  # if there is position
                if position["entryPrice"] > position["liquidationPrice"]:
                    return True

    def closeOpenedPositions(devise, ordersIds):
        if len(ordersIds) > 0:
            idsString = dumps(ordersIds).replace(" ", "")
            idsString = quote(idsString)
            return BinanceFutures.getClient().futures_cancel_orders(
                symbol=devise,
                orderIdList=idsString
            )
        return None

    def getClient():
        if BinanceFutures.client == None:
            BinanceFutures.client = Client(BinanceFutures.apiKey, BinanceFutures.apiSecret)
        return BinanceFutures.client