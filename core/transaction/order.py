from decimal import *

class Order:
    ORDER_TYPE_BUY = "buy"
    ORDER_TYPE_SELL = "sell"
    __TYPE_ALLOWED = ["buy", "sell"]
    __id = None
    __type = None
    __amount = None
    __price = None
    __status = None
    __time = None

    def __init__(self, id, type, amount, price, status, time, checkAllowed=True) -> None:
        if checkAllowed and type not in self.__TYPE_ALLOWED:
            raise Exception("Class Order accept only these values for argument 'type' : " + ", ".join(self.__TYPE_ALLOWED))
        self.__id = id
        self.__type = type
        self.__amount = Decimal(amount)
        self.__status = status
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
    def status(self):
        return self.__status

    @property
    def time(self):
        return self.__time

    @status.setter
    def status(self, value):
        self.__status = value

    @price.setter
    def price(self, value):
        self.__price = value

    @amount.setter
    def amount(self, value):
        self.__amount = value

    def __str__(self):
        str = f"\n--------------Order Status--------------\n"
        str += f"id : {self.id}\n"
        str += f"Date : {self.__time}\n"
        str += f"Type : {self.__type}\n"
        str += f"Amount : {self.__amount}\n"
        str += f"Status : {self.__status}\n"
        str += f"Price : {self.__price}\n"
        str += f"--------------Order Status--------------\n"
        return str