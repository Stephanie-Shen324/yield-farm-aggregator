from time import time, sleep


def main():
    # loop constantly and call data scraper every 5 mins
    attempts = 0
    while True:
        try:
            # 300 seconds = 5 minutes
            sleep(300 - time() % 300)
            # do work
            '''
            call function to scrape data from coin gecko and other site to then push to DB
            '''
            attempts = 0
        except Exception:
            attempts += 1
            # send notification to admin with error
            # continue for 3 attempts
            if attempts == 3:
                break
            else:
                continue
    return


if __name__ == "__main__":
    main()
