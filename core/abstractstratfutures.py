from core.abstractstrat import AbstractStrat
from core.transaction.leverageorder import LeverageOrder
from core.abstractindicators import AbstractIndicators
from decimal import *

class AbstractStratFutures(AbstractStrat):
    leverage = None
    orderInProgress = None
    walletInPosition = None

    def __init__(self, exchange, baseCurrency, tradingCurrency, base, trade, mainTimeFrame, leverage):
        super().__init__(exchange, baseCurrency, tradingCurrency, base, trade, mainTimeFrame)
        self.leverage = leverage
        self.walletInPosition = 0

    def run(self, client, apiKey, apiSecret):
        #TODO : wallet need to be changed when we place order
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
        if self.orderInProgress != None and self.exchange.orderIsLiquidated(self.orderInProgress.id):
            print("Order " + self.orderInProgress.id + " is liquidated")
            self.orderInProgress = None
        else:
            self.applyStrat(msg)
    
    def applyStrat(self, msg):
        currentIndex = self.exchange.historic[self.mainTimeFrame].last_valid_index()
        if self.orderInProgress != None:
            stopLossHitted = False
            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                stopLossHitted = self.stopLossLongPrice(currentIndex) >= self.exchange.historic[self.mainTimeFrame]['close'][currentIndex]
            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT:
                stopLossHitted = self.stopLossShortPrice(currentIndex) <= self.exchange.historic[self.mainTimeFrame]['close'][currentIndex]
            if stopLossHitted:
                print("Order " + self.orderInProgress.id + " is closed because stop loss is hitted")
                self.exchange.closeOrder(self.orderInProgress.id)
                self.orderInProgress = None
                return None
        #apply strat
        if self.exchange.isCandleClosed(msg):
            if self.orderInProgress == None:
                longCondition = self.longOpenConditions(currentIndex)
                shortCondition = self.shortOpenConditions(currentIndex)
                if longCondition > 0:
                    #Open Long order
                    amount = Decimal(self.wallet.base * longCondition / 100) / self.exchange.historic[self.mainTimeFrame]['close'][currentIndex]
                    order = self.exchange.longOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                    return None
                if longCondition == 0 and shortCondition > 0:
                    #Open Short order
                    amount = Decimal(self.wallet.base * shortCondition / 100) / self.exchange.historic[self.mainTimeFrame]['close'][currentIndex]
                    order = self.exchange.shortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                    return None

            else:
                #TODO : for the moment, closed partial order don't work. Only closed 100% is allow
                if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                    longCloseCondition = self.longCloseConditions(currentIndex)
                    if longCloseCondition>0:
                        #Close long order
                        order = self.exchange.closeOrder(self.orderInProgress.id)
                        print("Order " + self.orderInProgress.id + " is closed because close long condition is hitted")
                        self.orderInProgress = None
                        return None
                if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT:
                    shortCloseCondition = self.shortCloseConditions(currentIndex)
                    if shortCloseCondition>0:
                        #Close short order
                        order = self.exchange.closeOrder(self.orderInProgress.id)
                        print("Order " + self.orderInProgress.id + " is closed because close long condition is hitted")
                        self.orderInProgress = None
                        return None
                return None
        return None

    def getPercentWalletInPosition(self, wallet):
        if self.walletInPosition == None or wallet.base == None or wallet.base == 0:
            return 0
        return Decimal(self.walletInPosition/wallet.base)*100
    
    def hasPercentWalletNotInPosition(self, percent, wallet):
        if wallet.base == None:
            return False
        return 100-self.getPercentWalletInPosition(wallet)>=percent

    def longOpenConditions(self, index):
        """
        To determine long condition.
        Must return the percent of Wallet to take position.
        """
        return 0

    def longCloseConditions(self, index):
        """
        To determine long close.
        Must return the percent of current long trade to close
        """
        return 100
        
    def shortOpenConditions(self, index):
        """
        To determine short condition.
        Must return the percent of Wallet to take position.
        """
        return 0
    
    def shortCloseConditions(self, index):
        """
        To determine short close.
        Must return the percent of current short trade to close
        """
        return 100
    
    def stopLossLongPrice(self, index):
        """
        To determine stop loss condition for long order
        Must return the price to stop loss, or none
        """
        return None
    
    def stopLossShortPrice(self, index):
        """
        To determine stop loss condition for short order
        Must return the price to stop loss, or none
        """
        return None