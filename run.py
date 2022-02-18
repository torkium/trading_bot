from src.strats.stratbtcfuture import StratBtcFuture as Strat
from core.exchanges.ccxtfutures import CCXTFutures as Exchange
from core.core import Core
from core.tools.logger import Logger

""" 
Sample code to launch strat in real mode
"""
Core.run(Strat, Exchange, Logger, "userconfig.yaml")
#Core.backtest(Strat, Exchange, Logger, "userconfig.yaml", "2020-06-25 02:00:00")