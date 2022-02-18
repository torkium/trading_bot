from core.abstractstrat import AbstractStrat
from core.exchanges.ccxtfutures import CCXTFutures
from core.transaction.leverageorder import LeverageOrder
from core.abstractindicators import AbstractIndicators
from decimal import *
from datetime import datetime
from core.tools.logger import Logger
import time
import csv

class AbstractStratFutures(AbstractStrat):
    leverage = None
    orderInProgress = None
    walletInPosition = None

    def __init__(self, exchange, userConfig):
        super().__init__(exchange, userConfig)
        self.leverage = userConfig.strat['leverage']
        self.walletInPosition = 0

    def run(self, userConfig):
        #TODO : wallet need to be changed when we place order
        self.exchange.apiKey = userConfig.api['key']
        self.exchange.apiSecret = userConfig.api['secret']
        self.exchange.fakeMode = False
        Logger.write("Getting historic, please wait...", Logger.LOG_TYPE_INFO)
        for timeFrame in self.timeFrames:
            self.exchange.historic[timeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), timeFrame, self.exchange.getStartHistory(timeFrame, AbstractIndicators.MAX_PERIOD), limit=AbstractIndicators.MAX_PERIOD).tail(AbstractIndicators.MAX_PERIOD)
        self.startWallet = self.wallet.getTotalAmount(self.exchange.historic[self.mainTimeFrame]['open'].iloc[0])
        self.minWallet = self.startWallet
        self.maxWallet = self.startWallet
        Logger.write("historic getted.", Logger.LOG_TYPE_INFO)
        while True:
            time.sleep(self.timeToSleep)
            for timeFrame in self.timeFrames:
                self.exchange.historic[timeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), timeFrame, self.exchange.getStartHistory(timeFrame, AbstractIndicators.MAX_PERIOD), None, True, limit=AbstractIndicators.MAX_PERIOD).tail(AbstractIndicators.MAX_PERIOD)
                self.setIndicators(timeFrame)

            if self.orderInProgress != None and self.orderInProgress.status != self.exchange.ORDER_STATUS_FILLED:
                order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.id)
                if self.exchange.isFilledOrder(order):
                    self.orderInProgress.status = self.exchange.ORDER_STATUS_FILLED
                    self.orderInProgress.price = self.exchange.getOrderPrice(order)
                    Logger.write("Order " + str(self.orderInProgress.id) + " is filled", Logger.LOG_TYPE_INFO)
                    Logger.write(str(self.orderInProgress), Logger.LOG_TYPE_INFO)
            if self.orderInProgress != None and self.exchange.orderIsLiquidated(self.orderInProgress.id):
                Logger.write("Order " + str(self.orderInProgress.id) + " is liquidated", Logger.LOG_TYPE_DEBUG)
                self.orderInProgress = None
            else:
                self.applyStrat()

    def backtest(self, userConfig, fromDate):
        fromTimestamp = datetime.timestamp(datetime.strptime(fromDate, "%Y-%m-%d %H:%M:%S"))-CCXTFutures.getSeconds(self.mainTimeFrame, AbstractIndicators.MAX_PERIOD)
        toTimestamp = datetime.timestamp(datetime.now())
        self.exchange.apiKey = userConfig.api['key']
        self.exchange.apiSecret = userConfig.api['secret']
        Logger.write("Getting historic, please wait...", Logger.LOG_TYPE_INFO)
        for timeFrame in self.timeFrames:
            self.exchange.historic[timeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), timeFrame, fromTimestamp*1000, limit=self.exchange.getMaxPeriod(timeFrame, fromTimestamp, toTimestamp)).tail(self.exchange.getMaxPeriod(timeFrame, fromTimestamp, toTimestamp))
            self.setIndicators(timeFrame)
        
        
        f = open('./backtest.csv', 'w', encoding='UTF8', newline="")
        writer = csv.writer(f, delimiter=';')
        headers = ['datetime', 'price', 'action', 'amount', 'fees', 'wallet', 'open', 'high', 'low', 'close', 'volume']
        indicatorsHeaders = []
        for key in AbstractIndicators.INDICATORS_KEYS:
            indicatorsHeaders.append(key)
        writer.writerow(headers+indicatorsHeaders)

        self.startWallet = self.wallet.getTotalAmount(self.exchange.historic[self.mainTimeFrame]['open'].iloc[0])
        self.minWallet = self.startWallet
        self.maxWallet = self.startWallet
        Logger.write("historic getted.", Logger.LOG_TYPE_INFO)
        startHistoryIndex = AbstractIndicators.MAX_PERIOD
        endHistoryIndex = len(self.exchange.historic[self.mainTimeFrame].index)-1
        allHistory = self.exchange.historic.copy()
        self.previousOrder = None
        previous_valid_index = None
        long_counter = 0
        short_counter = 0
        stop_loss_long_counter = 0
        stop_loss_short_counter = 0
        for i in range(startHistoryIndex, endHistoryIndex):
            csvLine = []
            maxIndex = AbstractIndicators.MAX_PERIOD+i
            if maxIndex > len(allHistory[self.mainTimeFrame].index):
                maxIndex = len(allHistory[self.mainTimeFrame].index)-1
            self.exchange.historic[self.mainTimeFrame] = allHistory[self.mainTimeFrame].iloc[i:maxIndex, :]
            
            endSubHistoryIndex = len(self.exchange.historic[self.mainTimeFrame].index)-1
            self.exchange.mockPrice = self.exchange.historic[self.mainTimeFrame]['close'][len(self.exchange.historic[self.mainTimeFrame].index)-1]
            dateToLog = self.exchange.historic[self.mainTimeFrame].last_valid_index()
            

            csvLine.append(dateToLog)
            csvLine.append("")
            for i in range(2,11):
                csvLine.append("")
            for key in AbstractIndicators.INDICATORS_KEYS:
                csvLine.append(self.exchange.historic[self.mainTimeFrame][key][dateToLog])
            csvLine[2]=""
            csvLine[3]=""
            csvLine[4]=""
            csvLine[5]=""
            csvLine[6]=self.exchange.historic[self.mainTimeFrame]['open'][dateToLog]
            csvLine[7]=self.exchange.historic[self.mainTimeFrame]['high'][dateToLog]
            csvLine[8]=self.exchange.historic[self.mainTimeFrame]['low'][dateToLog]
            csvLine[9]=self.exchange.historic[self.mainTimeFrame]['close'][dateToLog]
            csvLine[10]=self.exchange.historic[self.mainTimeFrame]['volume'][dateToLog]
            
            liquidateHitted = False
            stopLossHitted = False
            newOrder = self.orderInProgress != None and self.previousOrder != self.orderInProgress
            if not newOrder:
                if self.orderInProgress != None and self.exchange.orderIsLiquidated(self.orderInProgress.id):
                    Logger.write("Order " + str(self.orderInProgress.id) + " is liquidated", Logger.LOG_TYPE_DEBUG)
                    csvLine[2]="LIQUIDATE"
                    csvLine[5]=self.wallet.base
                    liquidateHitted = True
                    self.orderInProgress = None
                if not liquidateHitted and self.orderInProgress != None:
                    for orderId in self.orderInProgress.linkedOrdersIds:
                        if self.exchange.mockedOrder[orderId]['status'] != self.exchange.ORDER_STATUS_CLOSED:
                            stopLossHitted = False
                            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG and self.exchange.getLow(self.mainTimeFrame, dateToLog) <= self.exchange.mockedOrder[orderId]['price']:
                                stopLossHitted = True
                                stop_loss_long_counter += 1
                            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT and self.exchange.getHigh(self.mainTimeFrame, dateToLog) >= self.exchange.mockedOrder[orderId]['price']:
                                stopLossHitted = True
                                stop_loss_short_counter += 1
                            if stopLossHitted:
                                self.exchange.mockedOrder[orderId]['status'] = self.exchange.ORDER_STATUS_CLOSED
            
            if not liquidateHitted and not stopLossHitted and self.previousOrder != self.orderInProgress:
                if self.orderInProgress != None:
                    Logger.write("NEW ORDER AT " + str(self.orderInProgress.price) + "! WALLET WILL BE UPDATED", Logger.LOG_TYPE_INFO, dateToLog)
                    self.exchange.mockedOrder[self.orderInProgress.id]['fee']['cost'] = Decimal(0.04)*self.orderInProgress.amount*self.orderInProgress.price
                    self.wallet.base -= self.exchange.mockedOrder[self.orderInProgress.id]['fee']['cost']
                    if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                        long_counter += 1
                        csvLine[2]="LONG"
                    if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT:
                        short_counter += 1
                        csvLine[2]="SHORT"
                    csvLine[1]=self.orderInProgress.price
                    csvLine[3]=self.orderInProgress.amount
                    csvLine[4]=self.exchange.mockedOrder[self.orderInProgress.id]['fee']['cost']
                else:                                
                    self.exchange.mockedOrder[self.previousOrder.id]['fee']['cost'] = Decimal(0.04)*self.previousOrder.amount*self.exchange.getPrice(self.mainTimeFrame, previous_valid_index)
                    self.wallet.base -= self.exchange.mockedOrder[self.previousOrder.id]['fee']['cost']
                    csvLine[5]=self.wallet.base
                    csvLine[4]=self.exchange.mockedOrder[self.previousOrder.id]['fee']['cost']
                    stopLossHitted = len(self.previousOrder.linkedOrdersIds)
                    for orderId in self.previousOrder.linkedOrdersIds:
                        order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId)
                        if self.exchange.getOrderStatus(order) != self.exchange.ORDER_STATUS_CLOSED:
                            stopLossHitted = False
                    if not stopLossHitted:
                        Logger.write("ORDER WAS CLOSED AT " + str(self.exchange.getPrice(self.mainTimeFrame, previous_valid_index)) + "! WALLET WILL BE UPDATED", Logger.LOG_TYPE_INFO, dateToLog)
                        csvLine[1]=self.exchange.getPrice(self.mainTimeFrame, previous_valid_index)
                        csvLine[2]="CLOSE"
                    else:
                        Logger.write("STOP LOSS WAS HITTED AT " + str(self.exchange.mockedOrder[orderId]['price']) + "! WALLET WILL BE UPDATED", Logger.LOG_TYPE_INFO, dateToLog)
                        Logger.write(self.exchange.mockedOrder[orderId]['price'], Logger.LOG_TYPE_INFO, dateToLog)
                        csvLine[1]=self.exchange.mockedOrder[orderId]['price']
                        csvLine[2]="STOP LOSS"

                self.previousOrder = self.orderInProgress
            if not liquidateHitted:
                self.applyStrat()
            previous_valid_index = self.exchange.historic[self.mainTimeFrame].index[len(self.exchange.historic[self.mainTimeFrame].index)-1]
            if i == endSubHistoryIndex and self.orderInProgress != None:
                fees = Decimal(0.04)*self.orderInProgress.amount*self.exchange.getPrice(self.mainTimeFrame, i)
                if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.exchange.historic[self.mainTimeFrame]['close'][i]-self.orderInProgress.price)-fees
                else:
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.orderInProgress.price-self.exchange.historic[self.mainTimeFrame]['close'][i])-fees
                csvLine[5]=self.wallet.base
            writer.writerow(csvLine)
        Logger.write("From : " + str(allHistory[self.mainTimeFrame].first_valid_index()), Logger.LOG_TYPE_DEBUG)
        Logger.write("To : " + str(allHistory[self.mainTimeFrame].last_valid_index()), Logger.LOG_TYPE_DEBUG)
        Logger.write("long : " + str(long_counter), Logger.LOG_TYPE_DEBUG)
        Logger.write("short : " + str(short_counter), Logger.LOG_TYPE_DEBUG)
        Logger.write("SL long : " + str(stop_loss_long_counter), Logger.LOG_TYPE_DEBUG)
        Logger.write("SL short : " + str(stop_loss_short_counter), Logger.LOG_TYPE_DEBUG)
        Logger.write("Wallet : " + str(self.wallet), Logger.LOG_TYPE_DEBUG)

    def applyStrat(self):
        if self.orderInProgress != None:
            stopLossHitted = len(self.orderInProgress.linkedOrdersIds)>0
            stopLossOrder = None
            for orderId in self.orderInProgress.linkedOrdersIds:
                order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId)
                if self.exchange.getOrderStatus(order) != self.exchange.ORDER_STATUS_CLOSED:
                    stopLossHitted = False
                else:
                    stopLossOrder = order
            if stopLossHitted:
                Logger.write("Order " + str(self.orderInProgress.id) + " is closed because stop loss is hitted", Logger.LOG_TYPE_INFO)
                Logger.write("Waiting new closed candle to try to take position...", Logger.LOG_TYPE_INFO)
                if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.exchange.getOrderPrice(stopLossOrder)-self.orderInProgress.price)-self.exchange.getOrderFeeCost(stopLossOrder)
                else:
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.orderInProgress.price-self.exchange.getOrderPrice(stopLossOrder))-self.exchange.getOrderFeeCost(stopLossOrder)
                self.orderInProgress = None
                self.waitNextClosedCandle = True
                return None
        #apply strat
        last_history_index = self.exchange.historic[self.mainTimeFrame].last_valid_index()
        if self.waitNextClosedCandle:
            if self.currentHistoryIndex == last_history_index:
                return None
            Logger.write("New closed candle. Waiting valid condition to take position...", Logger.LOG_TYPE_INFO)
            self.waitNextClosedCandle = False
        self.currentHistoryIndex = last_history_index
        price = self.exchange.getPrice(self.mainTimeFrame, self.currentHistoryIndex)
        if self.orderInProgress == None:
            longCondition = self.longOpenConditions(self.currentHistoryIndex)
            shortCondition = self.shortOpenConditions(self.currentHistoryIndex)
            if longCondition > 0:
                #Open Long order
                amount = Decimal(str(self.wallet.base * longCondition / 100)) / price
                self.wallet.base -= self.wallet.base * longCondition / 100
                orderId = self.exchange.longOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                self.orderInProgress = LeverageOrder(orderId, self.leverage, LeverageOrder.ORDER_TYPE_LONG, amount, price, self.exchange.ORDER_STATUS_NEW, datetime.now())
                self.wallet.base -= self.exchange.getOrderFeeCost(self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId))
                if self.stopLossLongPrice() != None:
                    orderId = self.exchange.stopLossLongOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage, self.stopLossLongPrice())
                    self.orderInProgress.addLinkedOrder(orderId)
                Logger.write("Order " + str(self.orderInProgress.id) + " is required", Logger.LOG_TYPE_INFO)
                Logger.write(str(self.orderInProgress), Logger.LOG_TYPE_INFO)
                return None
            if longCondition == 0 and shortCondition > 0:
                #Open Short order
                amount = Decimal(str(self.wallet.base * shortCondition / 100)) / price
                self.wallet.base -= self.wallet.base * shortCondition / 100
                orderId = self.exchange.shortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                self.orderInProgress = LeverageOrder(orderId, self.leverage, LeverageOrder.ORDER_TYPE_SHORT, amount, price, self.exchange.ORDER_STATUS_NEW, datetime.now())
                self.wallet.base -= self.exchange.getOrderFeeCost(self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId))
                if self.stopLossShortPrice() != None:
                    orderId = self.exchange.stopLossShortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage, self.stopLossShortPrice())
                    self.orderInProgress.addLinkedOrder(orderId)
                Logger.write("Order " + str(self.orderInProgress.id) + " is required", Logger.LOG_TYPE_INFO)
                Logger.write(str(self.orderInProgress), Logger.LOG_TYPE_INFO)
                return None
        else:
            #TODO : for the moment, closed partial order don't work. Only closed 100% is allow
            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_LONG:
                longCloseCondition = self.longCloseConditions(self.currentHistoryIndex)
                if longCloseCondition>0:
                    #Close long order
                    orderId = self.exchange.closeLongOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage)
                    order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId)
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.exchange.getOrderPrice(order)-self.orderInProgress.price)-self.exchange.getOrderFeeCost(order)
                    self.exchange.closeOpenedPositions(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.linkedOrdersIds)
                    Logger.write("Order " + str(self.orderInProgress.id) + " is closed because long close condition is filled", Logger.LOG_TYPE_INFO)
                    self.orderInProgress = None
                    self.waitNextClosedCandle = True
                    return None
            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT:
                shortCloseCondition = self.shortCloseConditions(self.currentHistoryIndex)
                if shortCloseCondition>0:
                    #Close short order
                    orderId = self.exchange.closeShortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage)
                    order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId)
                    self.wallet.base += (self.orderInProgress.amount*self.orderInProgress.price) + self.orderInProgress.amount*self.orderInProgress.leverage*(self.orderInProgress.price-self.exchange.getOrderPrice(order))-self.exchange.getOrderFeeCost(order)
                    self.exchange.closeOpenedPositions(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.linkedOrdersIds)
                    Logger.write("Order " + str(self.orderInProgress.id) + " is closed because short close condition is filled", Logger.LOG_TYPE_INFO)
                    self.orderInProgress = None
                    self.waitNextClosedCandle = True
                    return None
            return None
        return None

    def getPercentWalletInPosition(self, wallet):
        if self.walletInPosition == None or wallet.base == None or wallet.base == 0:
            return 0
        return Decimal(str(self.walletInPosition/wallet.base))*100

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

    def stopLossLongPrice(self):
        """
        To determine stop loss condition for long order
        Must return the price to stop loss, or none
        """
        return None

    def stopLossShortPrice(self):
        """
        To determine stop loss condition for short order
        Must return the price to stop loss, or none
        """
        return None