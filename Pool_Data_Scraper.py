# Imports
import pandas as pd
from web3 import Web3
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pool import Pool

# Initialise graphQL client
sample_transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
    verify=True, retries=5, )
client = Client(transport=sample_transport)

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
data_log = open("data.log", "a")

# Grab data from our sheet and read it into a Pandas dataframe

def scrape_data() -> [Pool]:
    googleSheetId = '1LcgMMQVS-8JktTChpWyX34p79KN5jWxBWJGCFITARpw'
    worksheetName = 'Sheet1'
    URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
        googleSheetId,
        worksheetName
    )
    df = pd.read_csv(URL)

    # Data cleaning
    df.drop(['#', 'Audits', 'Pool', 'IL Risk', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'URL',
             'https://www.coingecko.com/en/yield-farming'], axis=1, inplace=True, errors='ignore')
    df = df.dropna()
    df['Returns(Estimated)'] = df['Returns(Estimated)'].str.split('%').str[0]
    df.rename(columns={'Returns(Estimated)': 'Returns'}, inplace=True)

    pools = []
    size = df.shape[0]
    x = 0
    while x < size:
        row = df.iloc[x]
        protocol = str(row["Asset"]).strip().split("(")[0].strip()
        assets = []
        for asset in str(row["Collateral"]).strip().split(" "):
            assets.append(asset)
        tvl = str(row["Value Locked"]).strip()
        tvl = float(tvl[1:].replace(',', ''))
        apy = float(row["Returns"])

        # add basic IL functionality
        '''
        If no. of assets == 1:
            IL risk = None
        Else if all of the assets are stablecoin:
            IL risk = None
        Else if any of the assets are a stablecoin:
            IL risk = Medium
        Otherwise:
            IL risk = high
        '''
        stable_coins = ['1GOLD', 'ALCX', 'ALUSD', 'BUSD', 'BITCHY', 'BITUSD', 'BITGOLD', 'BITEUR', 'BVND', 'BGBP',
                        'CUSD', 'CONST', 'CEUR', 'DAI', 'DGD', 'DGX', 'DPT', 'EURS', 'EURT', 'EOSDT', 'EBASE',
                        'FEI', 'FRAX', 'FLUSD', 'GUSD', 'HGT', 'HUSD', 'ITL', 'IDRT', 'KBC', 'LUSD', 'MUSD', 'MTR',
                        'MDO', 'MDS', 'OUSD', 'PAX', 'PAR', 'QC', 'RSR', 'RSV', 'SUSD', 'SBD', 'TUSD', 'TRYB', 'TRIBE',
                        'UEYH', 'USDT', 'USDX', 'UST', 'USDC', 'USDS', 'USDN', 'USDK', 'USDH', 'USNBT', 'USDB', 'USDQ',
                        'USDP', 'USDL', 'USDFL', 'USDEX', 'UETH', 'VAI', 'XSGD', 'XCHF', 'XEUR', 'XAUR', 'ZUSD']
        IL_flag = 'UNASSIGNED'
        num_stablecoins = 0

        for asset in assets:
            if asset in stable_coins:
                num_stablecoins += 1

        if len(assets) == 1:
            IL_flag = 'None'
        elif num_stablecoins == len(assets):
            IL_flag = 'Low'
        elif num_stablecoins >= 1:
            IL_flag = 'Medium'
        else:  # Asset number bigger than 1, no assets are stablecoins
            IL_flag = 'High'
        # print(assets, IL_flag)
        tmp_pool = Pool(assets, protocol, None, None, None, apy, tvl, IL_flag)
        pools.append(tmp_pool)
        x += 1
    return pools


def scrape_sushi_pools() -> [Pool]:
    pools = []

    sushi_file = open("sushiswap.pools", "r")
    sushi_pools = {}
    for line in sushi_file:
        split = line.split()
        if len(split) != 2:
            continue
        sushi_pools[split[0]] = split[1].strip()

    for pool in sushi_pools:
        asset_list = pool.split("/")
        token0 = get_erc20_contract_address(asset_list[0])
        token1 = get_erc20_contract_address(asset_list[1])
        if token0 is None or token1 is None:
            continue
        pool_contract_address = Web3.toChecksumAddress(sushi_pools[pool])
        json_string = ""
        with open("balanceOf_ABI.json", "r") as json_abi:
            for line in json_abi:
                json_string = json_string + line
        json_abi.close()
        ABI = json.loads(json_string)
        token0_contract = w3.eth.contract(Web3.toChecksumAddress(token0), abi=ABI)
        token1_contract = w3.eth.contract(Web3.toChecksumAddress(token1), abi=ABI)
        token0_raw_balance = token0_contract.functions.balanceOf(pool_contract_address).call()
        token1_raw_balance = token1_contract.functions.balanceOf(pool_contract_address).call()
        token0_decimal = get_erc20_decimal(token0)
        token1_decimal = get_erc20_decimal(token1)
        token0_balance = token0_raw_balance/10**token0_decimal
        token1_balance = token1_raw_balance/10**token1_decimal
        token0_value = eth_to_usd(get_price_in_eth(asset_list[0], token0_balance))
        token1_value = eth_to_usd(get_price_in_eth(asset_list[1], token1_balance))
        total_value_locked = token0_value + token1_value
        print(asset_list)
        print(total_value_locked)







    return pools


def get_price_in_eth(token_symbol: str, quantity: float):
    if token_symbol == "WETH":
        return quantity
    pool_assets = "{}/WETH".format(token_symbol)
    inverted = False
    if pool_assets not in uniswap_pools:
        pool_assets = "WETH/{}".format(token_symbol)
        print(token_symbol + str(quantity))
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
    response = client.execute(query)
    pair = response['pair']
    if inverted:
        value = float(pair['reserve0']) / float(pair['reserve1'])
    else:
        value = float(pair['reserve1']) / float(pair['reserve0'])
    return value*quantity


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
    response = client.execute(query)
    pair = response['pair']
    value = float(pair['reserve0']) / float(pair['reserve1'])
    return value * eth_value


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
    response = client.execute(query)
    pair = response['pair']
    # Check symbols match
    if pair['token{}'.format(token)]['symbol'] != token_symbol:
        return None
    else:
        token_address = pair['token{}'.format(token)]['id']
    return token_address


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
