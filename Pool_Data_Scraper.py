# Imports
import pandas as pd
import pymongo
import dns
import pprint
from pool import Pool


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
    print(size)
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
        tmp_pool = Pool(assets, protocol, None, None, None, apy, tvl, 0)
        pools.append(tmp_pool)
        x += 1
    return pools
