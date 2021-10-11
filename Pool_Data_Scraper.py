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
    ###     
       # List of our hand selected pools
    selected_data = [
       ['Sushi (SUSHI)',['WBTC','WETH']],
       ['Venus (XVS)',['BTC']],
       ['Venus (XVS)',['ETH']],
       ['Aave (AAVE)',['AAVE','WETH']], 
       ['Venus (XVS)',['BNB']],
       ['Sushi (SUSHI)',['DAI','WETH']],
       ['Sushi (SUSHI)',['SUSHI','WETH']],
       ['Venus (XVS)',['USDT']],
       ['Sushi (SUSHI)',['WETH','USDT']],
       ['Venus (XVS)',['BUSD']],
       ['Auto (AUTO)',['CAKE']],
       ['Venus (XVS)',['USDC']],
       ['Auto (AUTO)',['BTCB']],
       ['Sushi (SUSHI)',['YFI','WETH']],
       ['Auto (AUTO)',['WBNB']],
       ['Auto (AUTO)',['ETH']],
       ['Venus (XVS)',['DOT']],
       ['Kyber Network Crystal (KNC)',['USDC','USDT']],
       ['Kyber Network Crystal (KNC)',['WBTC','WETH']],
       ['Kyber Network Crystal (KNC)',['WETH','USDT']],
       ['Auto (AUTO)',['WBNB','AUTO']],
       ['Venus (XVS)',['XRP']],
       ['Auto (AUTO)',['WBNB','BTCB']],
       ['Auto (AUTO)',['WBNB','CAKE']],
       ['Auto (AUTO)',['WBNB','BUSD']],
       ['Auto (AUTO)',['USDT']],
       ['Auto (AUTO)',['BUSD']],
       ['Kyber Network Crystal (KNC)',['WBTC','USDT']],
       ['Venus (XVS)',['DAI']],
       ['Venus (XVS)',['BCH']],
       ['Auto (AUTO)',['ETH','BETH']],
       ['Venus (XVS)',['LINK']],
       ['Kyber Network Crystal (KNC)',['WETH','KNC']],
       ['Rally (RLY)',['WETH','RLY']],
       ['Auto (AUTO)',['WBNB','ETH']],
       ['Auto (AUTO)',['DOT']],
       ['Harvest Finance (FARM)',['WETH','USDT']],
       ['Mirror Protocol (MIR)',['MUSO','UST']],
       ['Tokenlon (LON)',['LON','WETH']],
       ['Sushi (SUSHI)',['WETH','CRV']]
    ] 

    # Grabs the indices at which the full list of pools match our hand selection
    indices = []
    for index, row in df.iterrows():
      for i in range(len(selected_data)):
          if selected_data[i][0] == row.Asset and selected_data[i][1] == row.Collateral:
            indices.append(index)

    # Only include our selected pools, currently is not exclusive of similar pools
    df = df.loc[indices]
    df = df.reset_index(drop = True)

    ###

        #Jack's IL calculation
        IL = IL_calc(assets)
#         print(assets)
#         print(IL)
        tmp_pool = Pool(assets, protocol, None, None, None, apy, tvl, IL)
        pools.append(tmp_pool)
        x += 1
    return pools

# print(scrape_data())
  
