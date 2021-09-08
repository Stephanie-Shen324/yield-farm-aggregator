from web3 import Web3
import json
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Initialise Web3 client
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))


# Load in ABI for BSC
def load_abi(token_address):
    url_eth = "https://api.bscscan.com/api"
    contract_address = Web3.toChecksumAddress(token_address)
    API_ENDPOINT = url_eth + "?module=contract&action=getabi&address=" + str(contract_address)
    r = requests.get(url=API_ENDPOINT)
    response = r.json()
    print(response['result'])
    abi = json.loads(response['result'])
    return abi


# Initialise PancakeSwap pool data
pancake_pools = {}
pools_file = open("pancake.pools", "r")
for line in pools_file:
    split = line.split()
    pancake_pools[split[0]] = split[1].strip()
pools_file.close()

# Initialise log file
pancake_data_log = open("bep20_data.log", "a")


def get_bep20_decimal(token_contract_address: str):
    ABI = load_abi(token_contract_address)
    contract = w3.eth.contract(Web3.toChecksumAddress(token_contract_address), abi=ABI)
    decimal = contract.functions.decimals().call()
    return decimal


def get_bep20_contract(token_symbol: str):
    pass


def bnb_to_usd(bnb_value):
    pass


def get_price_in_bnb(token_symbol: str, quantity: float):
    if "BNB" in token_symbol:
        return quantity
    pool_assets = "{}/WBNB".format(token_symbol)
    inverted = False
    if pool_assets not in pancake_pools:
        pool_assets = "WBNB/{}".format(token_symbol)
        inverted = True
    try:
        pair_id = pancake_pools[pool_assets]
    except KeyError:
        pancake_data_log.write("Token not in UniSwap Pools: {}\n".format(token_symbol))
        return None
    abi = load_abi(pair_id)
    contract_address = w3.toChecksumAddress(pair_id)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    reserves = contract.functions.getReserves().call()
    token0 = contract.functions.token0().call()
    token1 = contract.functions.token1().call()
    print(len(token0))
    token0_decimal = w3.eth.contract(address=token0, abi=load_abi(token0)).functions.decimals().call()
    print(token0_decimal)


get_price_in_bnb("ETH", 1)
