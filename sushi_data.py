from web3 import Web3
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from pool import Pool
import time
from datetime import datetime
from erc20 import get_price_in_eth, get_erc20_decimal, get_erc20_contract_address, eth_to_usd

# Initialise SushiSwap graphQL client
sample_transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/zippoxer/sushiswap-subgraph-fork',
    verify=True, retries=5, )
sushi_client = Client(transport=sample_transport)

# Initialise SushiSwap pool address info
sushi_file = open("sushiswap.pools", "r")
sushi_pools = {}
for line in sushi_file:
    split = line.split()
    if len(split) != 2:
        continue
    sushi_pools[split[0]] = split[1].strip()

# Initialise Web3 client
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/68e4933ac39740e48b29a222aeba109e'))

# Initialise log file
data_log = open("data.log", "a")


def scrape_sushi_pools() -> [Pool]:
    start = time.time()
    pools = []
    json_string = ""
    with open("balanceOf_ABI.json", "r") as json_abi:
        for line in json_abi:
            json_string = json_string + line
    json_abi.close()
    ABI = json.loads(json_string)
    for pool in sushi_pools:
        try:
            asset_list = pool.split("/")
            token0 = get_erc20_contract_address(asset_list[0])
            token1 = get_erc20_contract_address(asset_list[1])
            if token0 is None or token1 is None:
                continue

            total_value_locked = get_tvl(sushi_pools[pool])
            daily_trading_vol = get_pair_24h_volume(sushi_pools[pool])
            hrly_trading_vol = get_pair_hr_volume(sushi_pools[pool])
            daily_yield = calculate_yield(daily_trading_vol, total_value_locked)
            hr_yeild = calculate_yield(hrly_trading_vol, total_value_locked)

            pool_tmp = Pool(asset_list,  # Assets
                            "Sushi",  # Protocol
                            sushi_pools[pool],  # Contract address
                            "https://app.sushi.com/farm",  # Link to protocol
                            None,  # Safety rating (already on db)
                            daily_yield*365,  # APY
                            total_value_locked,  # TVL
                            None,  # Impermanent Loss TO BE IMPLEMENTED
                            hrly_trading_vol,  # Hourly trading volume
                            daily_trading_vol,  # Daily trading volume
                            hr_yeild,  # Hourly APY
                            daily_yield  # Daily APY
                            )
            pools.append(pool_tmp)
        except Exception as e:
            data_log.write("{}: Exception thrown: {}\n".format(datetime.now(), e))
            continue

    end = time.time()
    duration = end - start
    data_log.write("{}: grabbing data for Sushi pools took {} seconds\n".format(datetime.now(), duration))
    return pools


def get_pair_24h_volume(pair_addr):
    date = int(int(time.time()) / 86400) - 1
    id = "{}-{}".format(pair_addr, date)
    query = gql('''
  query {{
    pairDayData(
      id: "{}"
    ) {{
      dailyVolumeUSD
    }}
  }}
  '''.format(id))
    response = sushi_client.execute(query)
    vol = response['pairDayData']['dailyVolumeUSD']
    return float(vol)


def calculate_yield(trading_vol: float, tvl: float):
    fees = trading_vol * 0.0025
    yield_percent = fees / tvl
    yield_percent = yield_percent * 100
    return yield_percent


def get_pair_hr_volume(pair_addr):
    hr = int(time.time() / 3600) - 1
    id = "{}-{}".format(pair_addr, hr)
    query = gql('''
    query {{
       pairHourData (
        id: "{}"
      ) {{
        hourlyVolumeUSD
      }} 
    }}
    '''.format(id))
    response = sushi_client.execute(query)
    vol = response['pairHourData']['hourlyVolumeUSD']
    return float(vol)


def get_tvl(pair_addr):
    query = gql('''
    query {{
       pair (
        id: "{}"
      ) {{
        reserveUSD
      }} 
    }}
    '''.format(pair_addr))
    response = sushi_client.execute(query)
    tvl = response['pair']['reserveUSD']
    return float(tvl)

scrape_sushi_pools()
