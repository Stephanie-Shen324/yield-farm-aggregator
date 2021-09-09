
class FarmPool:

    def __init__(self, protocol: str, assets: [str], sc_addr: str):
        self.protocol = protocol
        self.assets = assets
        self.sc_addr = sc_addr
        self.__tvl = []
        self.__daily_yields = []
        self.__annual_yields = []
        self.reward_token = None
        self.__impermanent_loss = []
        self.rating = 0.0

    def add_tvl(self, tvl: float):
        if len(self.__tvl) < 30:
            self.__tvl.append(tvl)
        else:
            self.__tvl.append(tvl)
            self.__tvl.pop(0)

    def get_tvl(self):
        return self.__tvl

    def add_daily_yield(self, d_yield):
        if len(self.__daily_yields) < 30:
            self.__daily_yields.append(d_yield)
        else:
            self.__daily_yields.append(d_yield)
            self.__daily_yields.pop(0)

    def get_daily_yields(self):
        return self.__daily_yields

    def add_annual_yield(self, a_yield: float):
        if len(self.__annual_yields) < 30:
            self.__annual_yields.append(a_yield)
        else:
            self.__annual_yields.append(a_yield)
            self.__annual_yields.pop(0)

    def get_annual_yields(self):
        return self.__annual_yields

    def add_il(self, il:float):
        if len(self.__impermanent_loss) < 30:
            self.__impermanent_loss.append(il)
        else:
            self.__impermanent_loss.append(il)
            self.__impermanent_loss.pop(0)

    def get_il(self):
        return self.__impermanent_loss
