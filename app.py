from time import time, sleep
from Pool_Data_Scraper import scrape_data
from pool import Pool
from mongo_server import MongoServer
from mongodb_error import MongoDBException


def main():
    db_client = MongoServer()
    # loop constantly and call data scraper every 5 mins
    attempts = 0
    while True:
        try:
            # 300 seconds = 5 minutes
            print(300 - time() % 300)
            sleep(300 - time() % 300)
            # do work
            '''
            call function to scrape data from coin gecko and other site to then push to DB
            '''
            pools = scrape_data()
            print("{} number of pools with data to update".format(len(pools)))
            for pool in pools:
                response = db_client.update_pool(pool)
                if response != 0:
                    response = db_client.insert_pool(pool)
                    if response != 0:
                        raise MongoDBException(
                            "Error pushing data: pool: {} ({}) could not be updated or inserted".format(
                                pool.get_protocol(), pool.get_assets()))
            attempts = 0
        except Exception as e:
            attempts += 1
            # send notification to admin with error
            db_client.write_log("Exception thrown: {}".format(e))
            # continue for 3 attempts
            if attempts == 3:
                break
            else:
                continue

    return


if __name__ == "__main__":
    main()
