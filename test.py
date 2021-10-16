
from binance.client import Client
from core.userconfig import UserConfig
from urllib.parse import quote
from json import dumps

userConfig = UserConfig("userconfig.yaml")
client = Client(userConfig.binance_futures['api_key'], userConfig.binance_futures['api_secret'])
devise = "BTCUSDT"
leverage = 1
retour = client.futures_change_leverage(symbol=devise, leverage=leverage)
#print(retour)

"""
retour = client.create_test_order(
    symbol = devise, 
    side = Client.SIDE_SELL, 
    type = Client.FUTURE_ORDER_TYPE_STOP_MARKET, 
    timeInForce = Client.TIME_IN_FORCE_GTC, 
    quantity = 0.001,
    stopPrice = 53000
)
print(retour)
#"""

"""
retour = client.futures_cancel_order(
    symbol=devise,
    orderId=33439474357,
)
print(retour)
#"""
"""
retour = client.futures_create_order(
    symbol=devise,
    type=Client.FUTURE_ORDER_TYPE_MARKET,
    side=Client.SIDE_BUY,
    quantity=0.001
)
print(retour)
client.futures_create_order(
    symbol = devise, 
    side = Client.SIDE_SELL, 
    type = Client.FUTURE_ORDER_TYPE_STOP_MARKET, 
    timeInForce = Client.TIME_IN_FORCE_GTC, 
    quantity = 0.001,
    stopPrice = 53000
)
#"""
"""
retour = client.futures_position_information(
    symbol=devise
)
print(retour)
#"""
"""
retour = client.futures_cancel_order(
    orderId="33439474357",
    symbol=devise
)
print(retour)
#"""

#"""
ordersIds = []
order1 = client.futures_create_order(
    symbol = devise, 
    side = Client.SIDE_SELL, 
    type = Client.FUTURE_ORDER_TYPE_STOP_MARKET, 
    timeInForce = Client.TIME_IN_FORCE_GTC, 
    quantity = 0.001,
    stopPrice = 50000
)
order2 = client.futures_create_order(
    symbol = devise, 
    side = Client.SIDE_BUY, 
    type = Client.FUTURE_ORDER_TYPE_STOP_MARKET, 
    timeInForce = Client.TIME_IN_FORCE_GTC, 
    quantity = 0.001,
    stopPrice = 65000
)
ordersIds.append(order1["orderId"])
ordersIds.append(order2["orderId"])
idsString = dumps(ordersIds).replace(" ", "")
idsString = quote(idsString)
retour = client.futures_cancel_orders(
    symbol=devise,
    orderIdList=idsString
)
print(retour)
#"""