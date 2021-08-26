import pymongo
import dns
import pprint

# UPDATE <password> TO MONGODB USER PASSWORD
client = pymongo.MongoClient("mongodb+srv://admin:<password>@yieldfarmingdata.cclc0.mongodb.net/YieldFarmingData"
                             "?retryWrites=true&w=majority")


def main():
    print("client databases: ")
    for db in client.list_database_names():
        pprint.pprint(db)
    db = client.pool_db
    print()
    print("collections: ")
    for col in db.list_collection_names():
        pprint.pprint(col)
    col = db.safety_ratings

    print()
    print("rated protocols: ")
    for doc in col.find():
        print("{}: {}".format(doc['protocolName'], doc['rating']))

    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
