
from binance.client import Client
from core.userconfig import UserConfig

userConfig = UserConfig("userconfig.yaml")
client = Client(userConfig.binance_futures['api_key'], userConfig.binance_futures['api_secret'])
devise = "BTCUSDT"
leverage = 1
retour = client.futures_change_leverage(symbol=devise, leverage=leverage)
print(retour)

retour = client.create_test_order(
    symbol=devise,
    type=Client.FUTURE_ORDER_TYPE_MARKET,
    side=Client.SIDE_BUY,
    quantity=0.001
)
print(retour)

"""
retour = client.create_test_order(
    symbol=devise,
    type=Client.FUTURE_ORDER_TYPE_STOP_MARKET,
    side=Client.SIDE_SELL,
    stopPrice=54500,
    closePosition = True
)
print(retour)
#"""
"""
retour = client.futures_create_order(
    symbol=devise,
    type=Client.FUTURE_ORDER_TYPE_MARKET,
    side=Client.SIDE_SELL,
    quantity=0.001
)
#"""
print(retour)