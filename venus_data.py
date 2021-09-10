from web3 import Web3
import requests
from bep20 import load_abi

# Get pool info
venus_pools = {}
pool_file = open("venus.pools", "r")
for line in pool_file:
    split = line.split()
    venus_pools[split[1]] = split[0]
pool_file.close()

for pool in venus_pools:
    abi = load_abi(pool)
    print(abi)
