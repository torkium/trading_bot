from datetime import datetime
from decimal import *
from .order import Order

class LeverageOrder(Order):
    ORDER_TYPE_LONG = "long"
    ORDER_TYPE_SHORT = "short"
    ORDER_TYPE_CLOSE = "close"
    ORDER_TYPE_LIQUIDATE = "liquidate"
    __TYPE_ALLOWED = ["long", "short", "close", "liquidate"]
    __leverage = None
    __percentToClose = 100

    

    def __init__(self, leverage, type, amount, price, time) -> None:
        if type not in self.__TYPE_ALLOWED:
            raise Exception("Class LeverageOrder accept only these values for argument 'type' : " + ", ".join(self.__TYPE_ALLOWED))
        self.__leverage = leverage
        super().__init__(type, amount, price, time, False)

    @property
    def leverage(self):
        return self.__leverage

    @property
    def percentToClose(self):
        return self.__percentToClose

    @property
    def liquidationPrice(self):
        if self.type == LeverageOrder.ORDER_TYPE_LONG:
            return self.price - (self.price / self.__leverage)
        if self.type == LeverageOrder.ORDER_TYPE_SHORT:
            return self.price + (self.price / self.__leverage)
        return None

    def close(self, percent=100):
        if percent > self.percentToClose:
            percent = self.percentToClose
        if percent==0:
            return None
        self.__percentToClose -= percent

    def __str__(self):
        str = f"\n--------------Order Status--------------\n"
        str += f"Date : {self.time}\n"
        str += f"Type : {self.type}\n"
        str += f"Leverage : {self.__leverage}\n"
        str += f"Amount : {self.amount} {self.tradeCurrency}\n"
        str += f"Price : {self.price} {self.baseCurrency}\n"
        if self.type != LeverageOrder.ORDER_TYPE_CLOSE:
            str += f"Percent to close (%) : {self.__percentToClose}\n"
        str += f"--------------Order Status--------------\n"
        return str