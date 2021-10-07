from src.indicators.indicators import Indicators
from src.strats.stratbtcfuture import StratBtcFuture
from core.exchanges.binancefutures import BinanceFutures as Exchange
from binance.client import Client
from core.userconfig import UserConfig
from operator import itemgetter



#"""
#Sample code to launch strat in real mode
stratfuture = StratBtcFuture(Exchange, "USDT", "BTC", 1000, 0, "4h", 7)
userConfig = UserConfig("userconfig.yaml")
stratfuture.run(Client, userConfig.binance_futures['api_key'], userConfig.binance_futures['api_secret'])
#"""