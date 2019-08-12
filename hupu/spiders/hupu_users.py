# -*- coding: utf-8 -*-

import re
import time
import json
import scrapy
import logging
import datetime
import requests
from py2neo import Graph
import hupu.utils as utils
from hupu.settings import *
from urllib.parse import urlencode
from scrapy_redis.spiders import RedisSpider
from hupu.items import UserItem, TopicItem, User


class HupuUsersSpider(RedisSpider):
    name = 'hupu_users'
    allowed_domains = ['hupu.com']
    redis_key = 'hupu_users:start_urls'

    graph = Graph(NEO4J_URI, password=NEO4J_PWD)

    def start_requests(self):
        index_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/topics"
        client = utils.get_random_client(),
        params = {
            'all': '1',
            'clientId': utils.get_random_clientId(),
            'crt': int(time.time()*1000),
            'night': '0',
            'client': client,
            '_ssid': utils.get_random_ssid(),
            '_imei': utils.get_random_imei(),
            'time_zone': 'Asia/Shanghai',
            'android_id': client,
            }
        params["sign"] = utils.get_sign(params)

        yield scrapy.Request(
            url=index_url + "?" + urlencode(params),
            dont_filter=True,
            callback=self.get_topics_list,
        )

    def get_topics_list(self, response):
        """
        a list for all main topics
        :param response:
        :return:
        """
        cate_list = json.loads(response.body.decode())["data"]["list"]
        topic_list = []

        for cate in cate_list:
            for topic in cate["topics"]:
                topic_list.append(topic)

        for topic in topic_list:
            if topic.get("fid"):
                pass

            else:
                topic_id = topic.get("topic_id")
                for page in range(1, 21):
                    topics_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/topics/threads"
                    client = utils.get_random_client()
                    params = {
                        'clientId': utils.get_random_clientId(),
                        'crt': int(time.time()*1000),
                        'night': '0',
                        'stamp': 0,
                        '_ssid': utils.get_random_ssid(),
                        '_imei': utils.get_random_imei(),
                        'time_zone': 'Asia/Shanghai',
                        'tab_type': '2',
                        'client': client,
                        'topic_id': topic_id,
                        'page': page,
                        'android_id': client,
                    }
                    params["sign"] = utils.get_sign(params)
                    yield scrapy.Request(
                        url=topics_url + "?" + urlencode(params),
                        dont_filter=True,
                        callback=self.get_sub_topics,
                        meta={"topic_id": topic_id}
                    )

    def get_fid(self, topic_id):
        topic_info_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/topics/{}".format(topic_id)
        client = utils.get_random_client()
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
        }
        params = {
            'clientId': utils.get_random_clientId(),
            'crt': int(time.time() * 1000),
            'night': '0',
            'client': client,
            '_ssid': utils.get_random_ssid(),
            '_imei': utils.get_random_imei(),
            'time_zone': 'Asia/Shanghai',
            'android_id': client,
        }
        params["sign"] = utils.get_sign(params)
        res = requests.get(topic_info_url, headers=headers, params=params)
        fid = json.loads(res.text)["data"]["topic"]["fid"]
        return fid

    @staticmethod
    def get_interval_date(days, hourly=0):
        """
        according to interval days,get date form today
        :param days: Date of interval
        :param hourly: return date or Down to the hour
        :return:
        """
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=days)
        if hourly:
            date = (today - delta).strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = (today - delta).strftime("%Y-%m-%d")
        return date

    def get_sub_topics(self, response):
        """
        parse posts in sub_topics
        :param response:
        :return:
        """
        topic_id = response.meta["topic_id"]
        fid = self.get_fid(topic_id)
        posts_list = json.loads(response.body.decode())["data"]["list"]
        if not posts_list:
            return

        for post in posts_list:
            if post.get("is_ad", "") == 1:
                continue
            topic_data = TopicItem()
            topic_data["tid"] = post["tid"]
            launch_str = post["time"]
            if "天" in launch_str:
                days = int(re.search(r'\d+', launch_str).group())
                launch_time = self.get_interval_date(days)
            else:
                launch_time = self.get_interval_date(0)
            topic_data["launch_time"] = launch_time
            topic_data["title"] = post["title"]
            topic_data["user_name"] = post["user_name"]
            topic_data["update_time"] = self.get_interval_date(0, 1)
            yield topic_data

            posts_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/threads/getsThreadPostList"
            client = utils.get_random_client()
            params = {
                'fid': fid,
                'clientId': utils.get_random_clientId(),
                'crt': int(time.time()*1000),
                'night': '0',
                'maxpid': '',
                '_ssid': utils.get_random_ssid(),
                '_imei': utils.get_random_imei(),
                'sort': '0',
                'webp': '1',
                'time_zone': 'Asia/Shanghai',
                'tid': post["tid"],
                'offline': 'json',
                'show_type': '',
                'postAuthorPuid': '',
                'client': client,
                'page': '1',
                'android_id': client,
                'entrance': '9',
                'order': 'asc',
            }
            params["sign"] = utils.get_sign(params)
            yield scrapy.Request(
                url=posts_url + "?" + urlencode(params),
                callback=self.get_replies,
                priority=10,
                meta={"current_page": 1, "fid": fid, "tid": post["tid"]}
            )

    def get_replies(self, response):
        """
        parse replies in posts
        :param response:
        :return:
        """
        res_data = json.loads(response.body.decode())
        if not res_data["data"]["result"]["list"]:
            return
        current_page = int(response.meta["current_page"])
        all_page = int(res_data["data"]["result"]["all_page"])
        while current_page < all_page:
            current_page += 1
            posts_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/threads/getsThreadPostList"
            client = utils.get_random_client()
            params = {
                'fid': response.meta["fid"],
                'clientId': utils.get_random_clientId(),
                'crt': int(time.time() * 1000),
                'night': '0',
                'maxpid': '',
                '_ssid': utils.get_random_ssid(),
                '_imei': utils.get_random_imei(),
                'sort': '0',
                'webp': '1',
                'time_zone': 'Asia/Shanghai',
                'tid': response.meta["tid"],
                'offline': 'json',
                'show_type': '',
                'postAuthorPuid': '',
                'client': client,
                'page': current_page,
                'android_id': client,
                'entrance': '9',
                'order': 'asc',
            }
            params["sign"] = utils.get_sign(params)
            yield scrapy.Request(
                url=posts_url + "?" + urlencode(params),
                callback=self.get_replies,
                priority=10,
                meta={
                    "current_page": current_page,
                    "fid": response.meta["fid"],
                    "tid": response.meta["tid"],
                },
            )

        replies_list = res_data["data"]["result"]["list"]
        for reply in replies_list:
            user_url = "https://games.mobileapi.hupu.com/3/7.3.17/user/page"
            params = {
                "client": utils.get_random_client(),
            }
            formdata = {
                'puid': str(reply["puid"]),
                'time_zone': 'Asia/Shanghai',
                'client': utils.get_random_client(),
                'night': '0',
                'crt': str(int(time.time())),
                'advId': '4497039A-C3C3-4A56-8266-4032F636152D',
                'clientId': utils.get_random_clientId(),
                '_ssid': utils.get_random_ssid(),
            }
            formdata["sign"] = utils.get_sign(formdata)
            yield scrapy.FormRequest(
                url=user_url + "?" + urlencode(params),
                formdata=formdata,
                callback=self.parse_user_detail,
                priority=15,
                meta={"puid": int(reply["puid"])}
            )

    def parse_user_detail(self, response):
        """
        parse detail info page for users
        :param response:
        :return:
        """
        user_json = json.loads(response.body.decode())["result"]

        mongo_user = UserItem()  # save data to MongoDB
        mongo_user["puid"] = response.meta["puid"]
        mongo_user["nickname"] = user_json["nickname"]
        neo4j_user = User()  # save data to Neo4j
        neo4j_user.puid = str(response.meta["puid"])
        neo4j_user.name = user_json["nickname"]
        
        mongo_user["header_url"] = user_json["header"]
        mongo_user["level"] = user_json["level"]
        if re.search(r'\d+', user_json["reg_time_str"]):
            register_days = re.search(r'\d+', user_json["reg_time_str"]).group()
        else:
            register_days = 0
        mongo_user["register_date"] = self.get_interval_date(int(register_days))
        mongo_user["gender"] = user_json["gender"]
        mongo_user["location"] = user_json["location_str"]
        mongo_user["follow_count"] = int(user_json["follow_count"])
        mongo_user["fans_count"] = int(user_json["be_follow_count"])
        mongo_user["be_light_count"] = int(user_json["be_light_count"])
        mongo_user["be_recommend_count"] = int(user_json["be_recommend_count"])
        mongo_user["bbs_msg_count"] = int(user_json["bbs_msg_count"])
        mongo_user["bbs_post_count"] = int(user_json["bbs_post_count"])
        mongo_user["bbs_recommend_count"] = int(user_json["bbs_recommend_count"])
        mongo_user["news_comment_count"] = int(user_json["news_comment_count"])
        mongo_user["bbs_msg_url"] = user_json["bbs_msg_url"]
        mongo_user["bbs_post_url"] = user_json["bbs_post_url"]
        mongo_user["bbs_recommend_url"] = user_json["bbs_recommend_url"]
        mongo_user["news_comment_url"] = user_json["news_comment_url"]
        mongo_user["bbs_follow_url"] = user_json["bbs_follow_url"]
        bbs_follow = self.get_follow(mongo_user, neo4j_user)
        mongo_user["bbs_fans_url"] = user_json["bbs_be_follow_url"]
        bbs_fans = self.get_fans(mongo_user)
        mongo_user["bbs_job"] = user_json["bbs_job"]
        mongo_user["reputation"] = int(user_json["reputation"]["value"])
        mongo_user["update_time"] = self.get_interval_date(0, 1)

        yield mongo_user

        all_contacts = bbs_follow + bbs_fans
        if all_contacts:
            for user in all_contacts:
                user_url = "https://games.mobileapi.hupu.com/3/7.3.17/user/page"
                params = {
                    "client": utils.get_random_client(),
                }
                formdata = {
                    'puid': str(user["puid"]),
                    'time_zone': 'Asia/Shanghai',
                    'client': utils.get_random_client(),
                    'night': '0',
                    'crt': str(int(time.time())),
                    'advId': '4497039A-C3C3-4A56-8266-4032F636152D',
                    'clientId': utils.get_random_clientId(),
                    '_ssid': utils.get_random_ssid(),
                }
                formdata["sign"] = utils.get_sign(formdata)
                yield scrapy.FormRequest(
                    url=user_url + "?" + urlencode(params),
                    formdata=formdata,
                    callback=self.parse_user_detail,
                    priority=15,
                    meta={"puid": int(user["puid"])}
                )

    def get_follow(self, mongo_user, neo4j_user):
        """
        get list for follow
        """
        if mongo_user["follow_count"] == 0:
            return []

        logging.debug("follow_count: %s" % mongo_user["follow_count"])
        bbs_follow = []
        page = 1
        user_follow_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/user/getUserFollow"
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
        }
        while True:
            params = {
                'puid': mongo_user["puid"],
                'client': utils.get_random_client(),
                'page': page,
            }
            res = requests.get(user_follow_url, headers=headers, params=params)
            res_json = json.loads(res.text)
            batch_data = res_json["result"].get("list", [])
            for item in batch_data:
                item["nickname"] = item.pop("username")

            for item in batch_data:
                neo4j_follow_user = User()
                neo4j_follow_user.puid = str(item["puid"])
                neo4j_follow_user.name = item["nickname"]
                neo4j_user.follow.update(neo4j_follow_user)
            self.graph.merge(neo4j_user)

            bbs_follow.extend(batch_data)
            if res_json["result"]["nextPage"]:
                page += 1
            else:
                break

        return bbs_follow

    def get_fans(self, mongo_user):
        """
        get list for fans
        """
        if mongo_user["fans_count"] == 0:
            return []

        logging.debug("fans_count: %s" % mongo_user["fans_count"])
        bbs_fans = []
        page = 1
        user_fans_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/user/getUserBeFollow"
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
        }
        while True:
            params = {
                'puid': mongo_user["puid"],
                'client': utils.get_random_client(),
                'page': page,
            }
            res = requests.get(user_fans_url, headers=headers, params=params)
            res_json = json.loads(res.text)
            batch_data = res_json["result"].get("list", [])
            for item in batch_data:
                item["nickname"] = item.pop("username")

            # for item in batch_data:
            #     neo4j_fan_user = User()
            #     neo4j_fan_user.puid = str(item["puid"])
            #     neo4j_fan_user.name = item["username"]
            #     self.graph.merge(neo4j_fan_user)
            #     neo4j_fan_user.follow.update(neo4j_user)
            #     self.graph.push(neo4j_fan_user)

            bbs_fans.extend(batch_data)
            if res_json["result"]["nextPage"]:
                page += 1
            else:
                break
        return bbs_fans



