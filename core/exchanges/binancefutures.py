from binance.enums import HistoricalKlinesType
from binance.client import Client
from core.exchanges.binancespot import BinanceSpot
from decimal import *

class BinanceFutures(BinanceSpot):
    feesRate = Decimal(0.04/100)
    klines_type = HistoricalKlinesType.FUTURES
    client = None

    def longOrder(devise, amount, leverage, type=Client.FUTURE_ORDER_TYPE_MARKET):
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        return BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=Client.FUTURE_ORDER_TYPE_MARKET,
            side=Client.SIDE_BUY,
            quantity=amount
        )

    def shortOrder(devise, amount, leverage, type="MARKET"):
        BinanceFutures.getClient().futures_change_leverage(symbol=devise, leverage=leverage)
        return BinanceFutures.getClient().futures_create_order(
            symbol=devise,
            type=Client.FUTURE_ORDER_TYPE_MARKET,
            side=Client.SIDE_SELL,
            quantity=amount
        )

    def orderIsLiquidated(orderId):
        return None

    def closeOrder(orderId):
        return None
    
    def getClient():
        if BinanceFutures.client == None:
            BinanceFutures.client = Client()
        return BinanceFutures.client