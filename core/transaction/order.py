from decimal import *

class Order:
    ORDER_TYPE_BUY = "buy"
    ORDER_TYPE_SELL = "sell"
    __TYPE_ALLOWED = ["buy", "sell"]
    __id = None
    __type = None
    __amount = None
    __price = None
    __time = None

    def __init__(self, id, type, amount, price, time, checkAllowed=True) -> None:
        if checkAllowed and type not in self.__TYPE_ALLOWED:
            raise Exception("Class Order accept only these values for argument 'type' : " + ", ".join(self.__TYPE_ALLOWED))
        self.__id = id
        self.__type = type
        self.__amount = Decimal(amount)
        self.__price = Decimal(price)
        self.__time = time

    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__type

    @property
    def amount(self):
        return self.__amount

    @property
    def price(self):
        return self.__price

    @property
    def time(self):
        return self.__time

    def __str__(self):
        str = f"\n--------------Order Status--------------\n"
        str += f"Date : {self.__time}\n"
        str += f"Type : {self.__type}\n"
        str += f"Amount : {self.__amount} {self.__baseCurrency}\n"
        str += f"Price : {self.__price} {self.__tradeCurrency}\n"
        str += f"--------------Order Status--------------\n"
        return str