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
        historic['SMATREND'] = Indicators.setMainTrend("EMA", historic)
        historic['RSIEVOL'] = Indicators.setEvol('RSI', historic)
        historic['PRICEEVOL'] = Indicators.setEvol('close', historic)
        historic['VOLUMEEVOL'] = Indicators.setEvol('volume', historic)
        AbstractIndicators.INDICATORS_KEYS.append('EMATREND')
        AbstractIndicators.INDICATORS_KEYS.append('SMATREND')
        AbstractIndicators.INDICATORS_KEYS.append('RSIEVOL')
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
                slope = 100 * (historic[key_from][index] - historic[key_from][lastIndex]) / historic[key_from][lastIndex]
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