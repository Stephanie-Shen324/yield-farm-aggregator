# Imports
import pandas as pd
from pool import Pool
from IL_calculator import IL_calc

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
        #Three level IL calculation method
        # If no. of assets == 1:
        #     IL risk = None
        # Else if all of the assets are stablecoin:
        #     IL risk = None
        # Else if any of the assets are a stablecoin:
        #     IL risk = Medium
        # Otherwise:
        #     IL risk = high
        
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
        '''
        #Jack's IL calculation
        IL = IL_calc(assets)
        print(assets)
        print(IL)
        tmp_pool = Pool(assets, protocol, None, None, None, apy, tvl, IL)
        pools.append(tmp_pool)
        x += 1
    return pools

# print(scrape_data())
  
