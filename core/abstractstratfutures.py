from core.abstractstrat import AbstractStrat
from core.transaction.leverageorder import LeverageOrder
from core.abstractindicators import AbstractIndicators
from datetime import datetime
from core.tools.logger import Logger
import time

class AbstractStratFutures(AbstractStrat):
    leverage = None
    orderInProgress = None
    walletInPosition = None

    def __init__(self, exchange, userConfig):
        super().__init__(exchange, userConfig)
        self.leverage = userConfig.strat['leverage']
        self.walletInPosition = 0

    def run(self, client, userConfig):
        #TODO : wallet need to be changed when we place order
        self.exchange.apiKey = userConfig.api['key']
        self.exchange.apiSecret = userConfig.api['secret']
        self.client = client(self.exchange.apiKey, self.exchange.apiSecret)
        Logger.write("Getting historic, please wait...", Logger.LOG_TYPE_INFO)
        self.exchange.historic[self.mainTimeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.mainTimeFrame, self.exchange.getStartHistory(self.mainTimeFrame, AbstractIndicators.MAX_PERIOD)).tail(AbstractIndicators.MAX_PERIOD)
        self.startWallet = self.wallet.getTotalAmount(self.exchange.historic[self.mainTimeFrame]['open'].iloc[0])
        self.minWallet = self.startWallet
        self.maxWallet = self.startWallet
        Logger.write("historic getted.", Logger.LOG_TYPE_INFO)

        # print(self.exchange.getAllOrder())
        # sys.exit()
        # load current order in progress
        # currentPosition = self.exchange.getOpenOrders(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency))

        # print(currentPosition)
        # if float(currentPosition['positionAmt']) != 0.0:
        #     self.orderInProgress = LeverageOrder(
        #         0,
        #         currentPosition['leverage'],
        #         LeverageOrder.ORDER_TYPE_LONG if float(currentPosition['positionAmt']) > 0.0 else LeverageOrder.ORDER_TYPE_SHORT,
        #         float(currentPosition['positionAmt']),
        #         currentPosition['entryPrice'],
        #         self.exchange.ORDER_STATUS_FILLED,
        #         currentPosition['updateTime']
        #     )
        #     Logger.write("Loaded current position %s %s x %s" % (currentPosition['positionAmt'], self.tradingCurrency, currentPosition['leverage']), Logger.LOG_TYPE_INFO)


        while True:
            time.sleep(self.timeToSleep)
            self.exchange.historic[self.mainTimeFrame] = self.exchange.getHistoric(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.mainTimeFrame, self.exchange.getStartHistory(self.mainTimeFrame, AbstractIndicators.MAX_PERIOD), None, True).tail(AbstractIndicators.MAX_PERIOD)
            self.setIndicators(self.mainTimeFrame)
            if self.orderInProgress != None and self.orderInProgress.status != self.exchange.ORDER_STATUS_FILLED:
                order = self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.id)
                if self.exchange.getOrderStatus(order) == self.exchange.ORDER_STATUS_FILLED:
                    self.orderInProgress.status = self.exchange.ORDER_STATUS_FILLED
                    self.orderInProgress.amount = self.exchange.getOrderQuantity(order)
                    self.orderInProgress.price = self.exchange.getOrderPrice(order)
                    Logger.write("Order " + str(self.orderInProgress.id) + " is filled", Logger.LOG_TYPE_INFO)
                    Logger.write(str(self.orderInProgress), Logger.LOG_TYPE_INFO)
            if self.orderInProgress != None and self.exchange.orderIsLiquidated(self.orderInProgress.id):
                Logger.write("Order " + str(self.orderInProgress.id) + " is liquidated", Logger.LOG_TYPE_DEBUG)
                self.orderInProgress = None
            else:
                self.applyStrat()

        """
        # TODO : for websocket, but for the moment it don't works correctly
        Logger.write("Waitting new closed candle...", Logger.LOG_TYPE_INFO)
        self.exchange.waitNewCandle(self.newCandleCallback, self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.mainTimeFrame)
        """

    def newCandleCallback(self, msg):
        Logger.write(msg, Logger.LOG_TYPE_DEBUG)
        self.exchange.appendNewCandle(msg, self.mainTimeFrame, self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), AbstractIndicators.MAX_PERIOD)
        self.setIndicators(self.mainTimeFrame)
        if self.orderInProgress != None and self.exchange.orderIsLiquidated(self.orderInProgress.id):
            Logger.write("Order " + str(self.orderInProgress.id) + " is liquidated", Logger.LOG_TYPE_DEBUG)
            self.orderInProgress = None
            self.waitNextClosedCandle = True
        else:
            self.applyStrat(msg)

    def applyStrat(self):
        if self.orderInProgress != None:
            stopLossHitted = len(self.orderInProgress.linkedOrdersIds)>0
            for orderId in self.orderInProgress.linkedOrdersIds:
                if self.exchange.getOrderStatus(self.exchange.getOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), orderId)) != self.exchange.ORDER_STATUS_FILLED:
                    stopLossHitted = False
            if stopLossHitted:
                Logger.write("Order " + str(self.orderInProgress.id) + " is closed because stop loss is hitted", Logger.LOG_TYPE_INFO)
                Logger.write("Waiting new closed candle to try to take position...", Logger.LOG_TYPE_INFO)
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
                amount = float(self.wallet.base * longCondition / 100) / price
                orderId = self.exchange.longOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                self.orderInProgress = LeverageOrder(orderId, self.leverage, LeverageOrder.ORDER_TYPE_LONG, amount, price, self.exchange.ORDER_STATUS_NEW, datetime.now())
                if self.stopLossLongPrice() != None:
                    orderId = self.exchange.stopLossLongOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage, self.stopLossLongPrice())
                    self.orderInProgress.addLinkedOrder(orderId)
                Logger.write("Order " + str(self.orderInProgress.id) + " is required", Logger.LOG_TYPE_INFO)
                Logger.write(str(self.orderInProgress), Logger.LOG_TYPE_INFO)
                return None
            if longCondition == 0 and shortCondition > 0:
                #Open Short order
                amount = float(self.wallet.base * shortCondition / 100) / price
                orderId = self.exchange.shortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), amount, self.leverage)
                self.orderInProgress = LeverageOrder(orderId, self.leverage, LeverageOrder.ORDER_TYPE_SHORT, amount, price, self.exchange.ORDER_STATUS_NEW, datetime.now())
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
                    self.exchange.closeOpenedPositions(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.linkedOrdersIds)
                    self.orderInProgress = None
                    self.waitNextClosedCandle = True
                    return None
            if self.orderInProgress.type == LeverageOrder.ORDER_TYPE_SHORT:
                shortCloseCondition = self.shortCloseConditions(self.currentHistoryIndex)
                if shortCloseCondition>0:
                    #Close short order
                    # orderId = self.exchange.closeShortOrder(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.amount, self.leverage)
                    self.exchange.closeOrder(self.orderInProgress.__id)
                    self.exchange.closeOpenedPositions(self.exchange.getDevise(self.baseCurrency, self.tradingCurrency), self.orderInProgress.linkedOrdersIds)
                    self.orderInProgress = None
                    self.waitNextClosedCandle = True
                    return None
            return None
        return None

    def getPercentWalletInPosition(self, wallet):
        if self.walletInPosition == None or wallet.base == None or wallet.base == 0:
            return 0
        return float(self.walletInPosition/wallet.base)*100

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