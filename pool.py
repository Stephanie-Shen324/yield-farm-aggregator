class Pool:
    __assets = []
    __protocol = ""
    __sc_address = ""
    __link = ""
    __safety = 0.0
    __apy = 0.0
    __tvl = 0.0
    __hr_trading_vol = 0.0
    __daily_trading_vol = 0.0
    __impermanent_loss = None

    def __init__(self, assets: [str], protocol: str, sc_address: str, link: str, safety: float, apy: float, tvl: float,
                 il):
        self.__assets = assets
        self.__protocol = protocol
        self.__sc_address = sc_address
        self.__link = link
        self.__safety = safety
        self.__apy = apy
        self.__tvl = tvl
        self.__impermanent_loss = il
        # self.__hr_trading_vol = hr_vol
        # self.__daily_trading_vol = daily_vol

    def get_assets(self):
        return self.__assets


    def get_protocol(self):
        return self.__protocol

    def get_sc_address(self):
        return self.__sc_address

    def get_link(self):
        return self.__link

    def set_link(self, link):
        self.__link = link

    def get_safety(self):
        return self.__safety

    def set_safety(self, safety):
        self.__safety = safety

    def get_apy(self):
        return self.__apy

    def set_apy(self, apy):
        self.__apy = apy

    def get_tvl(self):
        return self.__tvl

    def set_tvl(self, tvl):
        self.__tvl = tvl

    def get_impermanent_loss(self):
        return self.__impermanent_loss

    def set_impermanent_loss(self, il):
        self.__impermanent_loss = il

    def to_dict(self):
        pool_dict = {'assets': self.__assets, 'protocol': self.__protocol, 'scAddress': self.__sc_address,
                     'link': self.__link, 'safety': self.__safety, 'apy': self.__apy, 'tvl': self.__tvl,
                     'il': self.__impermanent_loss, 'hrVol': self.__hr_trading_vol, 'dailyVol': self.__daily_trading_vol}

        return pool_dict
