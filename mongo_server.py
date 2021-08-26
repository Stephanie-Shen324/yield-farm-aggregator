import pymongo
from _datetime import datetime
from pool import Pool


class MongoServer(pymongo.MongoClient):

    def __init__(self, **kwargs):
        super().__init__("mongodb+srv://admin:admin@yieldfarmingdata.cclc0.mongodb.net/YieldFarmingData?retryWrites"
                         "=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        self.__log_file = open("server.log", "a")

    def insert_pool(self, pool: Pool):
        col = self.pool_db.pools
        pool_dict = pool.to_dict()

        # add a new attribute called "pool"
        # example format: "protocol asset1/asset2/asset3" and assets are sorted by name
        pool_dict["pool"] = pool_dict["protocol"] + ' ' + '/'.join(sorted(pool_dict["assets"]))

        try:
            col.insert_one(pool_dict)
            self.__log_file.write("{}: {} is now added.".format(datetime.now(), pool_dict["pool"]))
        except Exception as e:
            self.__log_file.write(
                "{}: {} could not be added. This could be because it already exists.".format(datetime.now(),
                                                                                             pool_dict["pool"]))

    def update_pool(self, pool: Pool):
        col = self.pool_db.pools
        # search db for this document
        pool_dict = pool.to_dict()
        pool_dict["pool"] = pool_dict["protocol"] + ' ' + '/'.join(sorted(pool_dict["assets"]))
        doc_to_update = col.find_one({"pool": pool_dict["pool"]})

        if doc_to_update is None:
            self.__log_file.write(
                "{}: {} does not exist. Try insert using insert_pools function.".format(datetime.now(),
                                                                                        pool_dict["pool"]))
        else:
            col.update_one(doc_to_update, {"$set": pool.to_dict()})
            self.__log_file.write("{}: {} is successfully updated.".format(datetime.now(),
                                                                           pool_dict["pool"]))

