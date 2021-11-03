from core.userconfig import UserConfig

class Core:

    @staticmethod
    def run(Strat, Exchange, Client, Logger, userConfigFile):
        userConfig = UserConfig(userConfigFile)
        Logger.SHOW_CONSOLE = userConfig.logs["console"]
        Logger.LOG_LEVEL = userConfig.logs["level"]
        Strat = Strat(Exchange, userConfig)
        Strat.run(Client, userConfig)