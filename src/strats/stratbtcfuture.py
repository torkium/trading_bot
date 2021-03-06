from core.abstractstratfutures import AbstractStratFutures
from src.indicators.indicators import Indicators
from decimal import *

class StratBtcFuture(AbstractStratFutures):

    def __init__(self, exchange, userConfig):
        super().__init__(exchange, userConfig)

    def setIndicators(self, timeframe):
        Indicators.RSI_OVERBOUGHT = 70
        Indicators.RSI_OVERSOLD = 30
        Indicators.setIndicators(self.exchange.historic[timeframe])

    def longOpenConditions(self, index):
        """
        To determine long condition.
        Must return the percent of Wallet to take position.
        """        
        if (self.step == "long" or self.step == "longwaiting") and self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == -1:
            self.step = "short"
            return 0
        if (self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == 1 or self.step == "long") and self.exchange.historic[self.timeFrames[0]]['RSIEVOL'][index] >= -1:
            self.step = "main"
            return 50
        return 0

    #To determine long close condition
    def longCloseConditions(self, index):
        """
        To determine long close.
        Must return the percent of current long trade to close
        """
        if self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == -1:
            self.step = "short"
            return 100
        return 0
        
    #To determine short open condition
    def shortOpenConditions(self, index):
        """
        To determine short condition.
        Must return the percent of Wallet to take position.
        """
        if (self.step == "short" or self.step == "shortwaiting") and self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == 1:
            self.step = "long"
            return 0
        if (self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == -1 or self.step == "short") and self.exchange.historic[self.timeFrames[0]]['RSIEVOL'][index] <= 1:
            self.step = "main"
            return 50
        return 0
    
    #To determine short close condition
    def shortCloseConditions(self, index):
        """
        To determine short close.
        Must return the percent of current short trade to close
        """
        if self.exchange.historic[self.timeFrames[0]]['EMA20100CROSSMODE'][index] == 1:
            self.step = "long"
            return 100
        return 0
    
    def stopLossLongPrice(self):
        """
        To determine stop loss price for long order
        Must return the price to stop loss, or none
        """
        #return None
        stopLossPercent = Decimal(6)
        return self.orderInProgress.price - self.orderInProgress.price*stopLossPercent/100
    
    def stopLossShortPrice(self):
        """
        To determine stop loss price for short order
        Must return the price to stop loss, or none
        """
        #return None
        stopLossPercent = Decimal(6)
        return self.orderInProgress.price + self.orderInProgress.price*stopLossPercent/100