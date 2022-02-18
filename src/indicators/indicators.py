from turtle import st
from core.abstractindicators import AbstractIndicators
import pandas as pd

class Indicators(AbstractIndicators):

    MAX_PERIOD = 400
    PERIODS = [20,50,100,200]
    
    def setIndicators(historic):
        AbstractIndicators.setIndicators(historic)
        for period in AbstractIndicators.PERIODS:
            period_string = str(period)
            historic['SMA' + period_string + 'EVOL'] = Indicators.setEvol('SMA' + period_string, historic)
            historic['SMA' + period_string + 'SLOPE'] = Indicators.setSlope('SMA' + period_string, historic)
            historic['EMA' + period_string + 'EVOL'] = Indicators.setEvol('EMA' + period_string, historic)
            historic['EMA' + period_string + 'SLOPE'] = Indicators.setSlope('EMA' + period_string, historic)
            AbstractIndicators.INDICATORS_KEYS.append('SMA' + period_string + 'EVOL')
            AbstractIndicators.INDICATORS_KEYS.append('SMA' + period_string + 'SLOPE')
            AbstractIndicators.INDICATORS_KEYS.append('EMA' + period_string + 'EVOL')
            AbstractIndicators.INDICATORS_KEYS.append('EMA' + period_string + 'SLOPE')
        historic['EMATREND'] = Indicators.setMainTrend("EMA", historic)
        historic['EMATRENDCROSSMODE'] = Indicators.setEmaTrendCrossMode("EMATREND", historic)
        historic['EMA20100CROSSMODE'] = Indicators.setEmaCrossMode("EMA20", "EMA100", historic)
        historic['EMA2050CROSSMODE'] = Indicators.setEmaCrossMode("EMA20", "EMA50", historic)
        historic['SMATREND'] = Indicators.setMainTrend("EMA", historic)
        historic['RSIEVOL'] = Indicators.setEvol('RSI', historic)
        historic['RSISTATESINCE'] = Indicators.setRsiStateSince('RSI', historic)
        historic['RSISMA14EVOL'] = Indicators.setEvol('RSISMA14', historic)
        historic['RSICROSSMODE'] = Indicators.setRsiCrossMode('RSI', historic)
        historic['PRICEEVOL'] = Indicators.setEvol('close', historic)
        historic['VOLUMEEVOL'] = Indicators.setEvol('volume', historic)
        AbstractIndicators.INDICATORS_KEYS.append('EMA20100CROSSMODE')
        AbstractIndicators.INDICATORS_KEYS.append('EMA2050CROSSMODE')
        AbstractIndicators.INDICATORS_KEYS.append('EMATREND')
        AbstractIndicators.INDICATORS_KEYS.append('EMATRENDCROSSMODE')
        AbstractIndicators.INDICATORS_KEYS.append('SMATREND')
        AbstractIndicators.INDICATORS_KEYS.append('RSIEVOL')
        AbstractIndicators.INDICATORS_KEYS.append('RSISTATESINCE')
        AbstractIndicators.INDICATORS_KEYS.append('RSISMA14EVOL')
        AbstractIndicators.INDICATORS_KEYS.append('RSICROSSMODE')
        AbstractIndicators.INDICATORS_KEYS.append('PRICEEVOL')
        AbstractIndicators.INDICATORS_KEYS.append('VOLUMEEVOL')
    
    @staticmethod
    def setEvol(key_from, historic):
        EVOL = []
        lastIndex = None
        lastEvol = 0
        for index in historic.index:
            if lastIndex != None:
                diff = historic[key_from][index] - historic[key_from][lastIndex]
                if lastEvol>0 and diff>0:
                    lastEvol += 1
                if lastEvol<0 and diff<0:
                    lastEvol -= 1
                if lastEvol>=0 and diff<0:
                    lastEvol = -1
                if lastEvol<=0 and diff>0:
                    lastEvol = 1
            lastIndex = index
            EVOL.append(lastEvol)

        return pd.Series(EVOL, index = historic.index)
    
    @staticmethod
    def setSlope(key_from, historic):
        SLOPE = []
        lastIndex = None
        slope = 0
        for index in historic.index:
            if lastIndex != None:
                slope = 1000 * (historic[key_from][index] - historic[key_from][lastIndex]) / historic[key_from][lastIndex]
            lastIndex = index
            SLOPE.append(slope)

        return pd.Series(SLOPE, index = historic.index)
    
    @staticmethod
    def setMainTrend(type, historic):
        TRENDS = []
        lastIndex = None
        for index in historic.index:
            trend = 0
            if lastIndex != None:
                if historic[type + "20"][index] >= historic[type + "50"][index] and historic[type + "50"][index] >= historic[type + "100"][index] and historic[type + "100"][index] >= historic[type + "200"][index]:
                    trend = 2
                if historic[type + "20"][index] <= historic[type + "50"][index] and historic[type + "50"][index] >= historic[type + "100"][index] and historic[type + "100"][index] >= historic[type + "200"][index]:
                    trend = 1

                if historic[type + "200"][index] >= historic[type + "100"][index] and historic[type + "100"][index] >= historic[type + "50"][index] and historic[type + "50"][index] >= historic[type + "20"][index]:
                    trend = -2
                if historic[type + "200"][index] <= historic[type + "100"][index] and historic[type + "100"][index] >= historic[type + "50"][index] and historic[type + "50"][index] >= historic[type + "20"][index]:
                    trend = -1
            lastIndex = index
            TRENDS.append(trend)

        return pd.Series(TRENDS, index = historic.index)

    
    @staticmethod
    def setRsiStateSince(key_from, historic):
        STATE = []
        previous_state = None
        actual_state = None
        state_counter = 0
        for index in historic.index:
            actual_state = "neutral"
            if historic[key_from][index] >= Indicators.RSI_OVERBOUGHT:
                actual_state = "overbought"
            if historic[key_from][index] <= Indicators.RSI_OVERSOLD:
                actual_state = "oversold"
            if previous_state != None:
                if previous_state == actual_state:
                    state_counter += 1
            STATE.append(state_counter)
            previous_state = actual_state

        return pd.Series(STATE, index = historic.index)

    
    @staticmethod
    def setRsiCrossMode(key_from, historic):
        STATE = []
        previous_state = None
        actual_state = None
        state_mode = None
        for index in historic.index:
            if historic[key_from][index] < 50:
                actual_state = "neutral_bottom"
            if historic[key_from][index] > 50:
                actual_state = "neutral_top"
            if historic[key_from][index] >= Indicators.RSI_OVERBOUGHT:
                actual_state = "overbought"
            if historic[key_from][index] <= Indicators.RSI_OVERSOLD:
                actual_state = "oversold"
            if previous_state != actual_state:
                if (previous_state == "neutral_bottom" or previous_state == "neutral_top") and actual_state == "overbought":
                    state_mode = 1
                if previous_state == "overbought" and (actual_state == "neutral_bottom" or actual_state == "neutral_top"):
                    state_mode = 2
                if (previous_state == "neutral_bottom" or previous_state == "neutral_top") and actual_state == "oversold":
                    state_mode = -1
                if previous_state == "oversold" and (actual_state == "neutral_bottom" or actual_state == "neutral_top"):
                    state_mode = -2
                if previous_state == "neutral_bottom" and actual_state == "neutral_top":
                    state_mode = 3
                if previous_state == "neutral_top" and actual_state == "neutral_bottom":
                    state_mode = -3
            else:
                state_mode = 0
            STATE.append(state_mode)
            previous_state = actual_state

        return pd.Series(STATE, index = historic.index)

    
    @staticmethod
    def setEmaTrendCrossMode(key_from, historic):
        STATE = []
        previous_state = None
        actual_state = None
        state_mode = 0
        for index in historic.index:
            actual_state = historic[key_from][index]
            if previous_state != None:
                state_mode = actual_state-previous_state
            STATE.append(state_mode)
            state_mode = 0
            previous_state = actual_state
        return pd.Series(STATE, index = historic.index)

    
    @staticmethod
    def setEmaCrossMode(first_ema, second_ema, historic):
        STATE = []
        previous_state = None
        state_mode = 0
        for index in historic.index:
            actual_first_lt_second = historic[first_ema][index] < historic[second_ema][index]
            if previous_state != None:
                if actual_first_lt_second == previous_state:
                    if actual_first_lt_second:
                        state_mode = -2
                    else:
                        state_mode = 2
                else:
                    if actual_first_lt_second:
                        state_mode = -1
                    else:
                        state_mode = 1
            STATE.append(state_mode)
            previous_state = actual_first_lt_second
        return pd.Series(STATE, index = historic.index)