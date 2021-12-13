
class Wallet:
    __baseCurrency = None
    __tradeCurrency = None
    __base = None
    __trade = None

    def __init__(self, baseCurrency, tradeCurrency, stratBase, startTrade=None) -> None:
        self.__baseCurrency = baseCurrency
        self.__tradeCurrency = tradeCurrency
        self.__base = float(stratBase)
        if startTrade == None:
            self.__trade = float(0)
        else:
            self.__trade = float(startTrade)

    @property
    def baseCurrency(self):
        return self.__baseCurrency

    @property
    def tradeCurrency(self):
        return self.__tradeCurrency

    @property
    def base(self):
        return self.__base

    @property
    def trade(self):
        return self.__trade

    @property
    def baseInPosition(self):
        return self.__baseInPosition

    def getPercentBase(self, price):
        if self.__trade == None:
            return 100
        totalAMount = self.getTotalAmount(price)
        if totalAMount == 0 or totalAMount == None:
            return 0
        return float(self.__base/self.getTotalAmount(price))*100

    def getPercentTrade(self, price):
        if self.__trade == None:
            return 0
        totalAMount = self.getTotalAmount(price)
        if totalAMount == 0 or totalAMount == None:
            return 0
        return float(self.getTradeInBaseCurrency(price)/self.getTotalAmount(price))*100

    def getTotalAmount(self, price):
        return self.getTradeInBaseCurrency(price) + self.__base

    def getTradeInBaseCurrency(self, price):
        return float(self.__trade*price)

    @base.setter
    def base(self, value):
        if value < 0:
            self.__base = float(0)
        else:
            self.__base = float(value)

    @trade.setter
    def trade(self, value):
        if value < 0:
            self.__trade = float(0)
        else:
            self.__trade = float(value)

    def __str__(self):
        str = f"\n--------------Wallet Status--------------\n"
        str += f"{self.__base} {self.__baseCurrency}\n"
        str += f"{self.__trade} {self.__tradeCurrency}\n"
        str += f"--------------Wallet Status--------------\n"
        return str

    def toString(self, price = None):
        str = f"\n--------------Wallet Status--------------\n"
        str += f"{self.__base} {self.__baseCurrency} ({self.getPercentBase(price)} %)\n"
        str += f"{self.__trade} {self.__tradeCurrency} ({self.getPercentTrade(price)} %)\n"
        str += f"Total : {self.getTotalAmount(price)} {self.__baseCurrency}\n"
        str += f"--------------Wallet Status--------------\n"
        return str