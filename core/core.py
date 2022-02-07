from core.userconfig import UserConfig

class Core:

    @staticmethod
    def run(Strat, Exchange, Logger, userConfigFile):
        userConfig = UserConfig(userConfigFile)
        Logger.SHOW_CONSOLE = userConfig.logs["console"]
        Logger.LOG_LEVEL = userConfig.logs["level"]
        Exchange.EXCHANGE_ID = userConfig.strat['exchange_id']
        Strat = Strat(Exchange, userConfig)
        Strat.run(userConfig)