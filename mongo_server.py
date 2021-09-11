import pymongo
from _datetime import datetime
from pool import Pool


class MongoServer(pymongo.MongoClient):

    def __init__(self, **kwargs):
        super().__init__("mongodb+srv://admin:admin@yieldfarmingdata.cclc0.mongodb.net/YieldFarmingData?retryWrites"
                         "=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        self.__log_file = open("db.log", "a")

    def insert_pool(self, pool: Pool) -> int:
        col = self.pool_db.pools_test
        pool_dict = pool.to_dict()

        # add a new attribute called "pool"
        # example format: "protocol asset1/asset2/asset3" and assets are sorted by name
        pool_dict["pool"] = pool_dict["protocol"] + ' ' + '/'.join(sorted(pool_dict["assets"]))

        try:
            col.insert_one(pool_dict)
            self.__log_file.write("{}: {} is now added.\n".format(datetime.now(), pool_dict["pool"]))
        except Exception as e:
            self.__log_file.write(
                "{}: {} could not be added. This could be because it already exists.\n".format(datetime.now(),
                                                                                               pool_dict["pool"]))
            return -1
        return 0

    def update_pool(self, pool):
        col = self.pool_db.pools
        try:
            print("finding {} in db".format(pool['pool']))
            doc_to_update = col.find_one({'pool': pool['pool']})
            if doc_to_update is None:
                print("doc_to_update is none")
                self.__log_file.write(
                    "{}: {} does not exist. Try insert using insert_pools function.\n".format(datetime.now(),
                                                                                              pool['pool']))
                return 1
            col.update_one(doc_to_update, {"$set": pool})
            print("pool updated")
            self.__log_file.write("{}: {} is successfully updated.\n".format(datetime.now(),
                                                                             pool['pool']))
            return 0
        except Exception as e:
            self.__log_file.write("{}: updating {} threw error...\n".format(datetime.now(), pool['pool']))
            self.__log_file.write(str(e))
            self.__log_file.write("\n")
            return 1

    def update_pool_redundant(self, pool: Pool) -> int:
        col = self.pool_db.pools_test
        # search db for this document
        pool_dict = pool.to_dict()
        pool_dict["pool"] = pool_dict["protocol"] + ' ' + '/'.join(sorted(pool_dict["assets"]))
        doc_to_update = col.find_one({"pool": pool_dict["pool"]})

        if doc_to_update is None:
            self.__log_file.write(
                "{}: {} does not exist. Try insert using insert_pools function.\n".format(datetime.now(),
                                                                                          pool_dict["pool"]))
            return 1
        else:
            if float(pool.get_tvl()) == float(doc_to_update["tvl"]) and float(pool.get_apy()) == float(
                    doc_to_update["apy"]) and pool.get_impermanent_loss() == doc_to_update["il"]:
                self.__log_file.write("{}: No updates for {}\n".format(datetime.now(), pool_dict["pool"]))

                return 0

            pool.set_safety(doc_to_update["safety"])
            pool.set_link(doc_to_update["link"])
            col.update_one(doc_to_update, {"$set": pool.to_dict()})
            self.__log_file.write("{}: {} is successfully updated.\n".format(datetime.now(),
                                                                             pool_dict["pool"]))
            return 0

    def get_pools(self) -> [Pool]:
        collection = self.pool_db.pools_test
        pools = []
        for doc in collection.find():
            tmp_pool = Pool(doc["assets"], doc["protocol"], doc["scAddress"], doc["link"], doc["safety"], doc["apy"],
                            doc["tvl"], doc["il"])
            pools.append(tmp_pool)
        return pools

    def write_log(self, text: str):
        self.__log_file.write(text + "\n")


# db = pymongo.MongoClient("mongodb+srv://admin:admin@yieldfarmingdata.cclc0.mongodb.net/YieldFarmingData?retryWrites"
#                          "=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
#
# col = db.pool_db.pools
# f = open("venus.pools", "r")
# for line in f:
#     split = line.split()
#     pool = split[1]
#     assets = split[0].split("/")
#     pool_dict = {"assets": assets,
#                  "protocol": "Venus",
#                  "pool": pool,
#                  "tvl": [0.0],
#                  "dailyTradingVol": [0.0],
#                  "hrlyTradingVol": [0.0],
#                  "DPY": [0.0],
#                  "HPY": [0.0],
#                  "APY": [0.0],
#                  "rewardToken": {"name": "",
#                                  "marketCap": 0.0,
#                                  "spread": 0.0,
#                                  "depth": [-1.0, 1.0]},
#                  "il": 0.0,
#                  "rating": 0.0,
#                  "days": [0],
#                  "hours": [0]
#                  }
#     print(pool_dict)
#     result = col.insert_one(pool_dict)
#     print(result.acknowledged)
# f.close()
