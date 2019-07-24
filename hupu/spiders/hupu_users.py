# -*- coding: utf-8 -*-

import re
import time
import json
import scrapy
import random
import logging
import datetime
import requests
import hupu.utils as utils
from urllib.parse import urlencode
from scrapy_redis.spiders import RedisSpider
from hupu.items import UserItem, TopicItem


class HupuUsersSpider(RedisSpider):
    name = 'hupu_users'
    allowed_domains = ['hupu.com']
    redis_key = 'hupu_users:start_urls'

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
        所有大话题列表
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

    def get_sub_topics(self, response):
        """
        单个话题下的帖子
        :param response:
        :return:
        """
        topic_id = response.meta["topic_id"]
        fid = self.get_fid(topic_id)
        posts_list = json.loads(response.body.decode())["data"]["list"]
        if not posts_list:
            return

        for post in posts_list:
            topic_data = TopicItem()
            topic_data["light_replys"] = post["light_replys"]
            topic_data["recommends"] = post["recommends"]
            topic_data["replys"] = post["replys"]
            topic_data["tid"] = post["tid"]
            launch_str = post["time"]
            if "天" in launch_str:
                today = datetime.datetime.now()
                days = int(re.search(r'\d+', launch_str).group())
                delta = datetime.timedelta(days=days)
                launch_time = (today-delta).strftime("%Y-%m-%d")
            else:
                launch_time = datetime.datetime.now().strftime("%Y-%m-%d")
            topic_data["launch_time"] = launch_time
            topic_data["title"] = post["title"]
            topic_data["user_name"] = post["user_name"]
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
        单个帖子下回复
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
                'client': utils.get_random_client_post(),
                'night': '0',
                'crt': str(int(time.time())),
                'advId': '4497039A-C3C3-4A56-8266-4032F636152D',
                'clientId': utils.get_random_clientId(),
                '_ssid': utils.get_random_ssid_post(),
            }
            formdata["sign"] = utils.get_sign(formdata)
            yield scrapy.FormRequest(
                url=user_url + "?" + urlencode(params),
                formdata=formdata,
                callback=self.parse_user_detail,
                priority=15,
                meta={"puid": reply["puid"]}
            )

    def parse_user_detail(self, response):
        """
        用户详情页
        :param response:
        :return:
        """
        user_json = json.loads(response.body.decode())["result"]

        user_data = UserItem()
        user_data["puid"] = response.meta["puid"]
        user_data["nickname"] = user_json["nickname"]
        user_data["header_url"] = user_json["header"]
        user_data["level"] = user_json["level"]
        user_data["register_days"] = int(re.search(r'\d+', user_json["reg_time_str"]).group())
        user_data["gender"] = user_json["gender"]
        user_data["location"] = user_json["location_str"]
        user_data["follow_count"] = int(user_json["follow_count"])
        user_data["fans_count"] = int(user_json["be_follow_count"])
        user_data["be_light_count"] = int(user_json["be_light_count"])
        user_data["be_recommend_count"] = int(user_json["be_recommend_count"])
        user_data["bbs_msg_count"] = int(user_json["bbs_msg_count"])
        user_data["bbs_post_count"] = int(user_json["bbs_post_count"])
        user_data["bbs_recommend_count"] = int(user_json["bbs_recommend_count"])
        user_data["news_comment_count"] = int(user_json["news_comment_count"])
        user_data["bbs_msg_url"] = user_json["bbs_msg_url"]
        user_data["bbs_post_url"] = user_json["bbs_post_url"]
        user_data["bbs_recommend_url"] = user_json["bbs_recommend_url"]
        user_data["news_comment_url"] = user_json["news_comment_url"]
        user_data["bbs_follow_url"] = user_json["bbs_follow_url"]
        user_data["bbs_followers"] = self.get_followers(user_data)
        user_data["bbs_fans_url"] = user_json["bbs_be_follow_url"]
        user_data["bbs_fans"] = self.get_fans(user_data)
        user_data["bbs_job"] = user_json["bbs_job"]
        user_data["reputation"] = int(user_json["reputation"]["value"])

        yield user_data

        all_contacts = user_data["bbs_followers"] + user_data["bbs_fans"]
        if all_contacts:
            for user in all_contacts:
                user_url = "https://games.mobileapi.hupu.com/3/7.3.17/user/page"
                params = {
                    "client": utils.get_random_client(),
                }
                formdata = {
                    'puid': str(user["puid"]),
                    'time_zone': 'Asia/Shanghai',
                    'client': utils.get_random_client_post(),
                    'night': '0',
                    'crt': str(int(time.time())),
                    'advId': '4497039A-C3C3-4A56-8266-4032F636152D',
                    'clientId': utils.get_random_clientId(),
                    '_ssid': utils.get_random_ssid_post(),
                }
                formdata["sign"] = utils.get_sign(formdata)
                yield scrapy.FormRequest(
                    url=user_url + "?" + urlencode(params),
                    formdata=formdata,
                    callback=self.parse_user_detail,
                    priority=15,
                    meta={"puid": str(user["puid"])}
                )

    def get_followers(self, user_data):
        """
        获取关注列表
        :param user_data:
        :return:
        """
        if user_data["follow_count"] == 0:
            return []

        logging.debug("follow_count: %s" % user_data["follow_count"])
        bbs_followers = []
        page = 1
        user_follow_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/user/getUserFollow"
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
        }
        while True:
            params = {
                'puid': user_data["puid"],
                'client': utils.get_random_client(),
                'page': page,
            }
            res = requests.get(user_follow_url, headers=headers, params=params)
            res_json = json.loads(res.text)
            bbs_followers.extend(res_json["result"]["list"])
            if res_json["result"]["nextPage"]:
                page += 1
            else:
                break
        return bbs_followers

    def get_fans(self, user_data):
        """
        获取粉丝列表
        :param user_data:
        :return:
        """
        if user_data["fans_count"] == 0:
            return []

        logging.debug("fans_count: %s" % user_data["fans_count"])
        bbs_fans = []
        page = 1
        user_fans_url = "https://bbs.mobileapi.hupu.com/1/7.3.17/user/getUserBeFollow"
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
        }
        while True:
            params = {
                'puid': user_data["puid"],
                'client': utils.get_random_client(),
                'page': page,
            }
            res = requests.get(user_fans_url, headers=headers, params=params)
            res_json = json.loads(res.text)
            bbs_fans.extend(res_json["result"]["list"])
            if res_json["result"]["nextPage"]:
                page += 1
            else:
                break
        return bbs_fans



