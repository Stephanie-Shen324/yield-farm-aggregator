from web3 import Web3
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Initialise uniswap graphQL client
sample_transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
    verify=True, retries=5, )
uniswap_client = Client(transport=sample_transport)

# Initialise UniSwap pool address data
uniswap_pools = {}
pools_file = open("uniswap.pools", "r")
for line in pools_file:
    split = line.split()
    uniswap_pools[split[0]] = split[1].strip()
pools_file.close()

# Initialise Web3 client
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/68e4933ac39740e48b29a222aeba109e'))

# Initialise log file
data_log = open("erc20_data.log", "a")


def get_erc20_decimal(token_contract_address: str):
    json_string = ""
    with open("decimal_ABI.json", "r") as json_abi:
        for line in json_abi:
            json_string = json_string + line
    json_abi.close()
    ABI = json.loads(json_string)
    contract = w3.eth.contract(Web3.toChecksumAddress(token_contract_address), abi=ABI)
    decimal = contract.functions.decimals().call()
    return decimal


def get_erc20_contract_address(token_symbol: str):
    uniswap_address = ""
    token = -1
    for assets in uniswap_pools:
        if token_symbol in assets:
            uniswap_address = uniswap_pools[assets]
            each_asset = assets.split("/")
            if each_asset[0] == token_symbol:
                token = 0
            else:
                token = 1
            break
    if token == -1:
        return None
    query = gql('''
    query {{
        pair(id: "{}"){{
          token0 {{
            id
            symbol
          }}
          token1 {{
            id
            symbol
          }}
        }}
    }}
    '''.format(uniswap_address))
    response = uniswap_client.execute(query)
    pair = response['pair']
    # Check symbols match
    if pair['token{}'.format(token)]['symbol'] != token_symbol:
        return None
    else:
        token_address = pair['token{}'.format(token)]['id']
    return token_address


def eth_to_usd(eth_value):
    pair_id = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"
    query = gql('''
        query {{
          pair(id: "{}"){{
            reserve0
            reserve1
        }}
        }}
        '''.format(pair_id))
    response = uniswap_client.execute(query)
    pair = response['pair']
    value = float(pair['reserve0']) / float(pair['reserve1'])
    return value * eth_value


def get_price_in_eth(token_symbol: str, quantity: float):
    if token_symbol == "WETH":
        return quantity
    pool_assets = "{}/WETH".format(token_symbol)
    inverted = False
    if pool_assets not in uniswap_pools:
        pool_assets = "WETH/{}".format(token_symbol)
        inverted = True
    try:
        pair_id = uniswap_pools[pool_assets]
    except KeyError:
        data_log.write("Token not in UniSwap Pools: {}\n".format(token_symbol))
        return None

    query = gql('''
    query {{
      pair(id: "{}"){{
        reserve0
        reserve1
    }}
    }}
    '''.format(pair_id))
    response = uniswap_client.execute(query)
    pair = response['pair']
    if inverted:
        value = float(pair['reserve0']) / float(pair['reserve1'])
    else:
        value = float(pair['reserve1']) / float(pair['reserve0'])
    return value * quantity
