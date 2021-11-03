from src.strats.stratbtcfuture import StratBtcFuture as Strat
from core.exchanges.binancefutures import BinanceFutures as Exchange
from binance.client import Client
from core.core import Core
from core.tools.logger import Logger

""" 
Sample code to launch strat in real mode
"""
Core.run(Strat, Exchange, Client, Logger, "userconfig.yaml")