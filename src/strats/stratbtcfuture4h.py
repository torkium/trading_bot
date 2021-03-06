from core.abstractstratfutures import AbstractStratFutures
from src.indicators.indicators import Indicators
from decimal import *

class StratBtcFuture(AbstractStratFutures):

    def __init__(self, exchange, userConfig):
        super().__init__(exchange, userConfig)

    def setIndicators(self, timeframe):
        Indicators.RSI_OVERBOUGHT = 72
        Indicators.RSI_OVERSOLD = 34
        Indicators.setIndicators(self.exchange.historic[timeframe])

    def longOpenConditions(self, index):
        """
        To determine long condition.
        Must return the percent of Wallet to take position.
        """
        if self.step == "main":     
            if self.exchange.historic[self.timeFrames[0]]['EMA20EVOL'][index] > 1 and self.exchange.historic[self.timeFrames[0]]['EMATREND'][index] == 2 and self.exchange.historic[self.timeFrames[0]]['RSI'][index] < Indicators.RSI_OVERBOUGHT and self.exchange.historic[self.timeFrames[0]]['RSIEVOL'][index] > 1 and self.hasPercentWalletNotInPosition(10, self.wallet):
                return 50
        return 0

    #To determine long close condition
    def longCloseConditions(self, index):
        """
        To determine long close.
        Must return the percent of current long trade to close
        """
        if self.step == "main":
            if (self.exchange.historic[self.timeFrames[0]]['EMA20EVOL'][index] == -1) or (self.exchange.historic[self.timeFrames[0]]['PRICEEVOL'][index] < -2 and self.exchange.historic[self.timeFrames[0]]['VOLUMEEVOL'][index] < -2):
                return 100 
            if 100*(self.exchange.historic[self.timeFrames[0]]['close'][index] - self.orderInProgress.price)/self.orderInProgress.price < -3:
                return 100
        return 0
        
    #To determine short open condition
    def shortOpenConditions(self, index):
        """
        To determine short condition.
        Must return the percent of Wallet to take position.
        """
        if self.step == "main":
            if self.exchange.historic[self.timeFrames[0]]['EMA20EVOL'][index] < -1 and self.exchange.historic[self.timeFrames[0]]['EMATREND'][index] == -2 and self.exchange.historic[self.timeFrames[0]]['RSI'][index] > Indicators.RSI_OVERSOLD and self.exchange.historic[self.timeFrames[0]]['RSIEVOL'][index] < -1 and self.hasPercentWalletNotInPosition(10, self.wallet):
                return 50
        return 0
    
    #To determine short close condition
    def shortCloseConditions(self, index):
        """
        To determine short close.
        Must return the percent of current short trade to close
        """
        if self.step == "main":
            if (self.exchange.historic[self.timeFrames[0]]['EMA20EVOL'][index] == 1) or (self.exchange.historic[self.timeFrames[0]]['PRICEEVOL'][index] > 1 and self.exchange.historic[self.timeFrames[0]]['VOLUMEEVOL'][index] > 1):
                return 100
        return 0
    
    def stopLossLongPrice(self):
        """
        To determine stop loss price for long order
        Must return the price to stop loss, or none
        """
        #return None
        stopLossPercent = Decimal(3)
        return self.orderInProgress.price - self.orderInProgress.price*stopLossPercent/100
    
    def stopLossShortPrice(self):
        """
        To determine stop loss price for short order
        Must return the price to stop loss, or none
        """
        #return None
        stopLossPercent = Decimal(2)
        return self.orderInProgress.price + self.orderInProgress.price*stopLossPercent/100