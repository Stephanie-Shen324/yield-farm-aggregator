# Imports
import pandas as pd
import pymongo
import dns
import pprint
from pool import Pool

# Grab data from our sheet and read it into a Pandas dataframe
googleSheetId = '1LcgMMQVS-8JktTChpWyX34p79KN5jWxBWJGCFITARpw'
worksheetName = 'Sheet1'
URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
    googleSheetId,
    worksheetName
)
df = pd.read_csv(URL)
print(df)
quit()

# Data cleaning
df.drop(['#', 'Audits', 'Pool', 'IL Risk', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'URL',
         'https://www.coingecko.com/en/yield-farming'], axis=1, inplace=True, errors='ignore')
df = df.dropna()
df['Returns(Estimated)'] = df['Returns(Estimated)'].str.split('%').str[0]
df.rename(columns={'Returns(Estimated)': 'Returns'}, inplace=True)


# Pool class for MongoDB
# class Pool:
#     __Asset = ""
#     __Collateral = ""
#     __Value_Locked = ""
#     __Returns = ""
#
#     def __init__(self, Asset: str, Collateral: str, Value_Locked: str, Returns: str):
#         self.__Asset = Asset
#         self.__Collateral = Collateral
#         self.__Value_Locked = Value_Locked
#         self.__Returns = Returns
#
#     def get_Asset(self):
#         return self.__Asset
#
#     def get_Collateral(self):
#         return self.__Collateral
#
#     def get_Value_Locked(self):
#         return self.__Value_Locked
#
#     def get_Returns(self):
#         return self.__Returns
#
#     def to_dict(self):
#         pool_dict = {'Asset': self.__Asset, 'Collateral': self.__Collateral, 'Value Locked': self.__Value_Locked,
#                      'Returns': self.__Returns}
#
#         return pool_dict

print(df)

