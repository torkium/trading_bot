from src.strats.stratbtcfuture import StratBtcFuture
from core.exchanges.binancefutures import BinanceFutures as Exchange
from binance.client import Client
from core.userconfig import UserConfig
from core.tools.logger import Logger
from datetime import datetime

"""
Sample code to launch strat in real mode
"""

#To show logs in console too
Logger.SHOW_CONSOLE = True
#To have specific filename for log file with date and hour of execution
Logger.FILENAME = "logs/log_" + datetime.now().strftime("%Y%m%d_%H%M%S")
#Get the user config from user config file
userConfig = UserConfig("userconfig.yaml")
#Get the strat
stratfuture = StratBtcFuture(Exchange, userConfig)
#Run the strat
stratfuture.run(Client, userConfig)