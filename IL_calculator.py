# !pip install defi
# !pip install beautifulsoup4
# !python -m pip install pymongo[srv]
# !pip install pycoingecko

import defi.defi_tools as dft
import pandas as pd
import pymongo
import dns
import pprint
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import time
from asset_list import dict_assets

cg = CoinGeckoAPI()
coin_market = cg.get_coins_markets(vs_currency='usd')
market_data = pd.DataFrame(coin_market)
market_data.set_index('id', inplace=True)
dict_cg = pd.Series(market_data.index, index=market_data.symbol.values).to_dict()
dict_dft = pd.Series(dft.geckoList().id.values, index=dft.geckoList().index).to_dict()
asset_dictionary = {**dict_cg, **dict_dft, **dict_assets}


# Calculates the percentage change of two numbers
# (percentage output is a decimal where 1 = 100%, works better with iloss calculator this way)
def percentage_change(start, end):
    """
  Calculates the percentage change of two numbers
  (percentage output is a decimal where 1 = 100%, works better with iloss calculator this way)
  """
    return (end - start) / start


def ratio(base_value, quote_value):
    return (1 + base_value) / (1 + quote_value)


def get_price_history(search):
    """
    Gets the historical price, market cap and volume data for a specified asset via Defi's geckoHistorical function,
    which grabs it straight from coingecko's API

  INPUTS: search: coingecko's historical API requires the NAME of an asset, however this function has been written
  such that the name or symbol of an asset can be entered

  OUTPUT: if the term entered is valid, it will return the historical dataframe for the asset, otherwise it will
  return an error message for invalid entry
    """
    # Try searching for the exact term entered (works if search term is the name of an asset)
    try:
        return dft.geckoHistorical(search.lower())
    # If nothing is found, try searching for that term in the dictionary and search coingecko for its corresponding
    # name (works if search term is the symbol of an asset)
    except Exception as e:
        if search.lower() in asset_dictionary.keys():
            return dft.geckoHistorical(asset_dictionary[search.lower()])
        # Return error message if nothing is found
        else:
            return e


def d_days_price_change(symbol, d):
    """
  Calculates the percentage price change of an asset between now and d days ago

  INPUTS:
  asset: name or symbol of asset as string
  d: number of days as integer

  OUTPUTS:
  Percentage change of an asset over the last d days
  """
    if type(symbol) == KeyError:
        return symbol
    else:
        data = get_price_history(symbol)
        d_days_ago = data.index[-1] - timedelta(days=d)
        data = data[data.index > d_days_ago]
        return percentage_change(data.price[0], data.price[-1])


def historical_iloss(base, quote, d):
    """
    Combines the above functions with Defi Tools' iloss function to give the actual impermanent loss percentage over
    the last d days

  INPUTS:
  base: base asset symbol
  quote: quote asset symbol
  d: days to look back

  OUTPUTS:
  Historical impermanent loss as a percentage
  """
    # If either the base or quote symbol are invalid, return None - this is for skipping over invalid assets

    if type(d_days_price_change(base, d)) == KeyError or type(d_days_price_change(quote, d)) == KeyError:

        return None
    else:
        return dft.iloss(ratio(d_days_price_change(base, d), d_days_price_change(quote, d)))


def IL_calc(assets):
    """
  assets: a list of assets
  """
    # No iloss if < 2 assets
    if len(assets) < 2:
        ILoss = None
    elif len(assets) > 2:
        ILoss = 'High'
    else:
        # Try iloss calculation, wait 1 second between each
        try:
            ILoss = historical_iloss(assets[0], assets[1], 30)
            time.sleep(1)
        # KeyError indicates missing asset data, append 'No data'
        except KeyError as e:
            ILoss = 'No data'
        # Most other errors indicate an unresponsive API on account of too many calls, try again 3 times with a 5
        # second wait
        except:

            tries = 3
            for i in range(tries - 1):
                try:
                    # time.sleep(5)
                    ILoss = historical_iloss(assets[0], assets[1], 30)
                except:
                    continue
                else:
                    break
            # Append 'No data' if it isn't working after three tries, wait five more seconds to let the API settle
            else:
                ILoss = 'Not Available/API Error'
                # time.sleep(5)
        return ILoss

print(IL_calc(["LINK", "USDT"]))