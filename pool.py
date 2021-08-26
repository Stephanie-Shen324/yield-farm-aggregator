class Pool:
    __assets = []
    __protocol = ""
    __sc_address = ""
    __link = ""
    __safety = 0.0
    __apy = 0.0
    __tvl = 0.0
    __impermanent_loss = 0.0

    def __init__(self, assets: [str], protocol: str, sc_address: str, link: str, safety: float, apy: float, tvl: float,
                 il: float):
        self.__assets = assets
        self.__protocol = protocol
        self.__sc_address = sc_address
        self.__link = link
        self.__safety = safety
        self.__apy = apy
        self.__tvl = tvl
        self.__impermanent_loss = il

    def get_assets(self):
        return self.__assets

    def get_protocol(self):
        return self.__protocol

    def get_sc_address(self):
        return self.__sc_address

    def get_link(self):
        return self.__link

    def get_safety(self):
        return self.__safety

    def get_apy(self):
        return self.__apy

    def get_trading_volume(self):
        return self.__tvl

    def get_impermanent_loss(self):
        return self.__impermanent_loss

    def to_dict(self):
        pool_dict = {'assets': self.__assets, 'protocol': self.__protocol, 'scAddress': self.__sc_address,
                     'link': self.__link, 'safety': self.__safety, 'apy': self.__apy, 'tvl': self.__tvl,
                     'il': self.__impermanent_loss}

        return pool_dict
