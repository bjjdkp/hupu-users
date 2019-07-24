# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from hupu.items import UserItem, TopicItem


class HupuPipeline(object):

    user_collection_name = 'users'
    topic_collection_name = 'topics'

    def __init__(self, mongo_uri, mongo_port, mongo_db, mongo_usr, mongo_pwd):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.mongo_usr = mongo_usr
        self.mongo_pwd = mongo_pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'hupu'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_usr=crawler.settings.get('MONGO_USR'),
            mongo_pwd=crawler.settings.get('MONGO_PWD'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_uri, port=self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.db.authenticate(self.mongo_usr, self.mongo_pwd, mechanism='SCRAM-SHA-1')

        self.db[self.user_collection_name].create_index("puid", unique=True)
        self.db[self.topic_collection_name].create_index("tid", unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            self.db[self.user_collection_name].update_one(
                {"puid": dict(item)["puid"]},
                {"$set": dict(item)},
                upsert=True,
            )
        elif isinstance(item, TopicItem):
            self.db[self.topic_collection_name].update_one(
                {"tid": dict(item)["tid"]},
                {"$set": dict(item)},
                upsert=True,
            )
        return item
