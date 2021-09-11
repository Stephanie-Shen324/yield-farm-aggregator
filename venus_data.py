from web3 import Web3
import requests
from pythonpancakes import PancakeSwapAPI
import time, datetime
from datetime import datetime

from bep20 import load_abi
from mongo_server import MongoServer

# Get pool info
venus_pools = {}
pool_file = open("venus.pools", "r")
for line in pool_file:
    split = line.split()
    venus_pools[split[1]] = split[0]
pool_file.close()

# Initialise Web3 Client
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

# Initialise PancakeSwapAPI
ps_API = PancakeSwapAPI()

# Query Venus pool info
mongo_client = MongoServer()
col = mongo_client.pool_db.pools
venus_pools = []
for p in col.find({"protocol": "Venus"}):
    venus_pools.append(p)

# Initialise log file
data_log = open("venus_data.log", "a")

def scrape_venus_pools():
    pools = []
    start = datetime.now()
    for pool in venus_pools:
        try:
            hr = int(time.time() / 3600) - 1
            day = int(time.time() / 86400) - 1
            abi = load_abi(pool['pool'])

            contract_address = w3.toChecksumAddress(pool['pool'])
            contract = w3.eth.contract(address=contract_address, abi=abi)
            if contract.functions.name().call() == "Venus BNB":
                underlying_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
            else:
                underlying_token = contract.functions.underlying().call()
            cash = contract.functions.getCash().call()
            total_supply = contract.functions.totalSupply().call()
            total_borrows = contract.functions.totalBorrows().call()
            decimals = contract.functions.decimals().call()

            # convert data to asset values
            total_supply_vBTC = total_supply/10**decimals  # in vBTC
            total_borrows_BTCB = total_borrows/10**18  ## in BTCB
            liquidity = cash/10**18  # in BTCB
            exchange_rate = total_supply/(total_borrows + liquidity)
            # Get asset price from pancakeswap
            try:
                asset_price = float(ps_API.tokens(underlying_token)['data']['price'])
            except requests.exceptions.HTTPError:
                data_log.write("{}: Cannot get asset price for {}".format(time.time(), underlying_token))
                continue
            # total value locked
            tvl = (total_supply/exchange_rate) * asset_price

            # trading vol (In venus, trading vol is the amount borrowed at any time)
            trading_vol = total_borrows * asset_price

            # yield
            block_supply_rate = contract.functions.supplyRatePerBlock().call() / 10 ** 18
            supply_rate = block_supply_rate * 10512000  # Average blocks per year as of 10/09/2021
            supply_rate = supply_rate * 100  # convert to %

            if day not in pool['days']:
                pool['dailyTradingVol'].append(trading_vol)
                pool['DPY'].append(supply_rate/365)
                pool['APY'].append(supply_rate)
                pool['days'].append(day)
            if hr not in pool['hours']:
                pool['tvl'].append(tvl)  # TVL added every hour but what if user wants to view it daily...?
                pool['hrlyTradingVol'].append(trading_vol)
                pool['HPY'].append(supply_rate/365*24)
                pool['hours'].append(hr)

            pools.append(pool)
        except Exception as e:
            data_log.write("{}: Exception thrown: {}\n".format(datetime.now(), e))
            continue
    end = datetime.now()
    duration = end - start
    data_log.write("{}: grabbing data for Venus pools took {} seconds\n".format(datetime.now(), duration))

    return pools
