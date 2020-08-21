
import csv
from pymongo import MongoClient


class Mongo(object):
    def __init__(self):
        self.local_mongo_user = "test"
        self.local_mongo_pwd = "test"
        self.local_host = "localhost:27017"
        self.local_client = MongoClient(self.local_host)
        self.local_db = self.local_client["hupu"]
        self.local_db.authenticate(self.local_mongo_user, self.local_mongo_pwd, mechanism='SCRAM-SHA-1')
        self.local_collection = self.local_db["users"]


mongo = Mongo()
source_users = mongo.local_collection.find()


user_headers = ["puid:ID", "name", ":LABEL"]
user_rows = set()

rel_headers = [":START_ID", ":END_ID", ":TYPE"]
rel_rows = set()

for item in source_users:
    print(item)
    user_rows.add((int(item["puid"]), item["nickname"], "User"))
    if item["bbs_fans"]:
        for fan in item["bbs_fans"]:
            user_rows.add((int(fan["puid"]), fan["username"], "User"))
            rel_rows.add((int(fan["puid"]), int(item["puid"]), "follow"))
            print("user_rows: %s" % len(user_rows))
            print("rel_rows: %s" % len(rel_rows))

    if item["bbs_followers"]:
        for follower in item["bbs_followers"]:
            user_rows.add((int(follower["puid"]), follower["username"], "User"))
            rel_rows.add((int(item["puid"]), int(follower["puid"]), "follow"))
            print("user_rows: %s" % len(user_rows))
            print("rel_rows: %s" % len(rel_rows))

with open('users.csv', 'w') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(user_headers)
    f_csv.writerows(user_rows)

with open('roles.csv', 'w') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(rel_headers)
    f_csv.writerows(rel_rows)







