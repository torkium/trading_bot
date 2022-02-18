from decimal import MAX_EMAX
import ta
import pandas as pd

class AbstractIndicators:
    
    INDICATORS_KEYS = []

    MAX_PERIOD = 400
    PERIODS = [20,50,100,200]
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_SLOW = 26
    MACD_FAST = 12
    MACD_SIGN = 9

    @staticmethod
    def setIndicators(historic):
        for period in AbstractIndicators.PERIODS:
            period_string = str(period)
            historic['SMA' + period_string] = ta.trend.sma_indicator(historic['close'], period)
            historic['EMA' + period_string] = ta.trend.ema_indicator(historic['close'], period)
            AbstractIndicators.INDICATORS_KEYS.append('SMA' + period_string)
            AbstractIndicators.INDICATORS_KEYS.append('EMA' + period_string)
        historic['RSI'] = ta.momentum.RSIIndicator(historic['close'], window=AbstractIndicators.RSI_PERIOD).rsi()
        historic['RSISMA14'] = ta.trend.sma_indicator(historic['RSI'], 14)
        historic['MACD'] = ta.trend.MACD(historic['close'], window_slow=AbstractIndicators.MACD_SLOW, window_fast=AbstractIndicators.MACD_FAST, window_sign=AbstractIndicators.MACD_SIGN).macd()
        historic['MACDDIFF'] = ta.trend.MACD(historic['close']).macd_diff()
        historic['MACDSIGN'] = ta.trend.MACD(historic['close']).macd_signal()
        AbstractIndicators.INDICATORS_KEYS.append('RSI')
        AbstractIndicators.INDICATORS_KEYS.append('RSISMA14')
        AbstractIndicators.INDICATORS_KEYS.append('MACD')
        AbstractIndicators.INDICATORS_KEYS.append('MACDDIFF')
        AbstractIndicators.INDICATORS_KEYS.append('MACDSIGN')