from core.wallet import Wallet
from core.abstractindicators import AbstractIndicators
from decimal import *

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

    def __init__(self, exchange, baseCurrency, tradingCurrency, base, trade, mainTimeFrame):
        self.exchange = exchange
        self.mainTimeFrame = mainTimeFrame
        self.wallet = Wallet(baseCurrency, tradingCurrency, base, trade)
        self.baseCurrency = baseCurrency
        self.tradingCurrency = tradingCurrency
        self.base = base
        self.trade = trade
        self.transactions = {}
        self.currentDrawdown = 0
        self.maxDrawdown = 0
        self.totalFees = 0
        self.stopLoss = 0

    
    def setIndicators(self, timeframe):
        return None

    def demo(self):
        """
        To launch strat in live demo mode
        """
        return None

    def run(self, client, apiKey, apiSecret):
        self.client = client(apiKey, apiSecret)
        self.exchange.historic[self.mainTimeFrame] = self.exchange.getHistoric(self.tradingCurrency, self.baseCurrency, self.mainTimeFrame, self.exchange.getStartHistory(self.mainTimeFrame, AbstractIndicators.MAX_PERIOD)).tail(AbstractIndicators.MAX_PERIOD)
        self.startWallet = self.wallet.getTotalAmount(self.exchange.historic[self.mainTimeFrame]['open'].iloc[0])
        self.minWallet = self.startWallet
        self.maxWallet = self.startWallet
        print("historic getted. Wait new closed candle...")
        self.exchange.waitNewCandle(self.newCandleCallback, self.tradingCurrency+self.baseCurrency, self.mainTimeFrame, apiKey, apiSecret)

    def newCandleCallback(self, msg):
        self.exchange.appendNewCandle(msg, self.mainTimeFrame, self.tradingCurrency+self.baseCurrency, AbstractIndicators.MAX_PERIOD)
        self.setIndicators(self.mainTimeFrame)
        return None

    def addHistory(self, timeframe):
        self.exchange.historic[timeframe] = self.exchange.getHistoric(self.tradingCurrency, self.baseCurrency, timeframe, self.startDate, self.endDate)

    def getLastHistoryIndex(self, index, timeframe):
        timeToReturn = None
        for key in self.exchange.historic[timeframe]:
            if key >= index:
                return timeToReturn
            timeToReturn = key