from web3 import Web3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import time
from datetime import datetime
from mongo_server import MongoServer

# Initialise SushiSwap graphQL client
sample_transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/zippoxer/sushiswap-subgraph-fork',
    verify=True, retries=5, )
sushi_client = Client(transport=sample_transport)

# Query SushiSwap pool info
mongo_client = MongoServer()
col = mongo_client.pool_db.pools
sushi_pools = []
for p in col.find({"protocol": "Sushi"}):
    sushi_pools.append(p)

# Initialise Web3 client
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/68e4933ac39740e48b29a222aeba109e'))

# Initialise log file
data_log = open("sushi_data.log", "a")


def scrape_sushi_pools():
    start = time.time()
    pools = []

    for pool in sushi_pools:
        try:
            hr = int(time.time() / 3600) - 1
            day = int(time.time() / 86400) - 1

            total_value_locked = get_tvl(pool["pool"])
            if day not in pool["days"]:
                # total_value_locked
                pool["tvl"].append(total_value_locked)
                if len(pool["tvl"]) > 30:
                    pool["tvl"].pop(0)
                # trading vol
                daily_trading_vol = get_pair_24h_volume(pool["pool"])
                pool["dailyTradingVol"].append(daily_trading_vol)
                if len(pool["dailyTradingVol"]) > 30:
                    pool["dailyTradingVol"].pop(0)
                # daily yield
                pool["DPY"].append(calculate_yield(daily_trading_vol, total_value_locked))
                if len(pool["DPY"]) > 30:
                    pool["DPY"].pop(0)
            if hr not in pool["hours"]:
                # trading vol
                hrly_trading_vol = get_pair_hr_volume(pool["pool"])
                pool["hrlyTradingVol"].append(hrly_trading_vol)
                if len(pool["hrlyTradingVol"]) > 169:
                    pool["hrlyTradingVol"].pop(0)
                # hourly yield
                pool["HPY"].append(calculate_yield(hrly_trading_vol, total_value_locked))
                if len(pool["HPY"]) > 169:
                    pool["HPY"].pop(0)

            daily_avg = 0
            for y in pool["DPY"]:
                daily_avg += y
            daily_avg = daily_avg/len(pool["DPY"])
            apy = daily_avg*365

            pool["APY"].append(apy)
            if len(pool["APY"]) > 30:
                pool["APY"].pop(0)

            pool["days"].append(day)
            pool["hours"].append(hr)

            pools.append(pool)
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
    fees = trading_vol * 0.0025  # SushiSwap LPs receive 0.25% of fees (0.005% is distributed to SUSHI Holders)
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
