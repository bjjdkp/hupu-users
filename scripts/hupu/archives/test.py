# --*-- coding:utf-8 --*--

# 部分数据写入图数据库

import time
import datetime
from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo
from pymongo import MongoClient

# graph = Graph("http://localhost:7474", password="942&op!UKVg2GQfL")
# graph.delete_all()


class User(GraphObject):
    __primarykey__ = 'puid'

    puid = Property()
    name = Property()
    follow = RelatedTo('User', 'follow')


class Mongo(object):
    def __init__(self):
        self.local_mongo_user = "root"
        self.local_mongo_pwd = "M09z%qWMvU9kQ!A5"
        self.local_host = "123.206.38.21:27017"
        self.local_client = MongoClient(self.local_host)
        self.local_db = self.local_client["admin"]
        self.local_db.authenticate(self.local_mongo_user, self.local_mongo_pwd, mechanism='SCRAM-SHA-1')
        self.local_collection = self.local_db["ip_source"]


mongo = Mongo()
s_time = time.time()

source_users = mongo.local_collection.find().limit(5)
print(time.time()-s_time)
for item in source_users:
    print(item)
# now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# mongo.local_collection.update_many(
#     {}, {'$set': {"update_time": now_time}},
# )

# for item in source_users:
#     print(item)


# u1 = User()
# u1.puid = "29776600"

# u2 = User()
# u2.puid = '123123123'
#
# u3 = User()
# u3.puid = '321321312'
#
# u4 = User()
# u4.puid = '111111111'


# u2.follow.update(u1)
# u2.follow.update(u3)
# u2.follow.update(u4)
# graph.merge(u2)
# graph.push(u2)

# a =graph.match((u1,))
# for i in a:
#     print(i)



# for source_user in source_users:
#     print(source_user["nickname"])
#     user = User()
#     user.puid = source_user["puid"]
#     user.name = source_user["nickname"]
#     if source_user["bbs_followers"]:
#         for follower in source_user["bbs_followers"]:
#             follower_user = User()
#             follower_user.puid = int(follower["puid"])
#             follower_user.name = follower["username"]
#             graph.merge(user)
#             user.follow.update(follower_user)
#             graph.push(user)
#
#     if source_user["bbs_fans"]:
#         for fan in source_user["bbs_fans"]:
#             fan_user = User()
#             fan_user.puid = int(fan["puid"])
#             fan_user.name = fan["username"]
#             graph.merge(fan_user)
#             fan_user.follow.update(user)
#             graph.push(fan_user)






