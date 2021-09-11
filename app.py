from time import time, sleep
from Pool_Data_Scraper import scrape_data
from pool import Pool
from sushi_data import scrape_sushi_pools
from venus_data import scrape_venus_pools
from mongo_server import MongoServer
from mongodb_error import MongoDBException


def main():
    db_client = MongoServer()
    attempts = 0
    while True:
        try:
            wait_time = 30
            print(wait_time - time() % wait_time)
            sleep(wait_time - time() % wait_time)
            # do work
            '''
            call function to scrape data from coin gecko and other site to then push to DB
            '''
            pools = scrape_sushi_pools()
            pools.extend(scrape_venus_pools())

            print("{} number of pools with data to update".format(len(pools)))
            for pool in pools:
                print("updating: {} {}".format(pool['protocol'], pool['assets']))
                response = db_client.update_pool(pool)
                if response != 0:
                    # response = db_client.insert_pool(pool)
                    if response != 0:
                        raise MongoDBException(
                            "Error pushing data: pool: {} ({}) could not be updated or inserted".format(
                                pool['protocol'], pool['assets']))
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
