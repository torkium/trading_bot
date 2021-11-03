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
        self.mainTimeFrame = userConfig.strat['timeframe']
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

    def demo(self):
        """
        To launch strat in live demo mode
        """
        return None

    def run(self, client, userConfig):
        self.exchange.apiKey = userConfig.api['key']
        self.exchange.apiSecret = userConfig.api['secret']
        self.client = client(self.exchange.apiKey, self.exchange.apiSecret)
        self.exchange.historic[self.mainTimeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.mainTimeFrame, self.exchange.getStartHistory(self.mainTimeFrame, AbstractIndicators.MAX_PERIOD)).tail(AbstractIndicators.MAX_PERIOD)
        self.startWallet = self.wallet.getTotalAmount(self.exchange.historic[self.mainTimeFrame]['open'].iloc[0])
        self.minWallet = self.startWallet
        self.maxWallet = self.startWallet
        Logger.write("historic getted. Wait new closed candle...", Logger.LOG_TYPE_INFO)
        self.exchange.waitNewCandle(self.newCandleCallback, self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.mainTimeFrame)

    def newCandleCallback(self, msg):
        self.exchange.appendNewCandle(msg, self.mainTimeFrame, self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), AbstractIndicators.MAX_PERIOD)
        self.setIndicators(self.mainTimeFrame)
        return None

    def addHistory(self, timeframe):
        self.exchange.historic[timeframe] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), timeframe, self.startDate, self.endDate)

    def getLastHistoryIndex(self, index, timeframe):
        timeToReturn = None
        for key in self.exchange.historic[timeframe]:
            if key >= index:
                return timeToReturn
            timeToReturn = key