from core.wallet import Wallet
from core.abstractindicators import AbstractIndicators
from decimal import *
from core.tools.logger import Logger

class AbstractStrat:
    exchange = False
    historic = False
    wallet = False
    step = "main"
    baseCurrency = None
    tradingCurrency = None
    mainTimeFrame = None
    startDate = None
    endDate = None
    base = None
    trade = None
    transactions = None
    history = None
    startWallet = None
    minWallet = None
    maxWallet = None
    currentDrawdown = None
    maxDrawdown = None
    totalFees = None
    timeToSleep = 300
    currentHistoryIndex = None
    waitNextClosedCandle = False

    def __init__(self, exchange, userConfig):
        self.exchange = exchange
        self.mainTimeFrame = userConfig.strat['timeframe'][0]
        self.timeFrames = userConfig.strat['timeframe']
        self.baseCurrency = userConfig.strat['base_currency']
        self.tradingCurrency = userConfig.strat['trade_currency']
        self.timeToSleep = userConfig.strat['time_to_sleep']
        self.base = userConfig.strat['wallet']['base']
        self.trade = userConfig.strat['wallet']['trade']
        self.wallet = Wallet(self.baseCurrency, self.tradingCurrency, self.base, self.trade)
        self.transactions = {}
        self.currentDrawdown = 0
        self.maxDrawdown = 0
        self.totalFees = 0
        self.stopLoss = 0

    
    def setIndicators(self, timeframe):
        return AbstractIndicators.setIndicators(self.exchange.historic[timeframe])

    def run(self, userConfig):
        return None

    def backtest(self, userConfig, fromDate):
        return None