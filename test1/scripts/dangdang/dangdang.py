# --*-- coding:utf-8 --*--
# 当当阅读器

import re
import json
import time
import requests


class DangDang(object):
    def __init__(self, epub_id):
        """
        :param epub_id: the id of book
        """
        self.url = "https://e.dangdang.com/media/api.go"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        }
        self.epub_id = epub_id

    def get_media_info(self):
        params = {
            "action": "getPcMediaInfo",
            "consumeType": "1",
            "platform": "3",
            "deviceType": "Android",
            "deviceVersion": "5.0.0",
            "channelId": "70000",
            "platformSource": "DDDS-P",
            "fromPaltform": "ds_android",
            "deviceSerialNo": "html5",
            "clientVersionNo": "5.8.4",
            "epubID": self.epub_id,
            "token": "",
            "wordSize": "2",
            "style": "2",
        }
        res = requests.get(self.url, headers=self.headers, params=params).text
        page_info = json.loads(res)["data"]["mediaPageInfo"]
        page_info = self.sort_dict(page_info)
        return page_info

    @staticmethod
    def sort_dict(data):
        """
        sorted and parse the key of dict
        :param data: source data of dict
        :return:
        """
        new_dict = {}
        for item in data:
            num = int(re.search(r'\d+', item).group())
            new_dict[num] = data[item]
        return sorted(new_dict.items())

    def get_chapter_info(self, c_id, p_index, l_index):
        """
        get content for each page
        :param c_id: chapter id
        :param p_index: page index
        :param l_index: location index
        :return:
        """
        params = {
            "action": "getPcChapterInfo",
            "epubID": self.epub_id,
            "permanentId": "20191016193600193257303706324182103",
            "consumeType": "1",
            "platform": "3",
            "deviceType": "Android",
            "deviceVersion": "5.0.0",
            "channelId": "70000",
            "platformSource": "DDDS-P",
            "fromPaltform": "ds_android",
            "deviceSerialNo": "html5",
            "clientVersionNo": "5.8.4",
            "token": "",
            "chapterID": c_id,
            "pageIndex": p_index,
            "locationIndex": l_index,
            "wordSize": "2",
            "style": "2",
            "autoBuy": "0",
            "chapterIndex": "",
        }

        res = requests.get(self.url, headers=self.headers, params=params).text
        pattern = re.compile(r'<span class=.*?style=\\\\\\"left:(\d+)px; bottom:(\d+)px; \\\\\\">(.*?)<\\\\/span>')

        data = pattern.findall(res)
        data = map(lambda x: (int(x[0]), int(x[1]), x[2]), data)
        data = sorted(data, key=lambda x: (-x[1], x[0]))

        content = ""
        for i in data:
            content += i[2]

        return content

    def run(self):
        page_info = self.get_media_info()
        for page in page_info:
            l_location = page[0]
            c_id = page[1]["chapterID"]
            p_index = page[1]["pageIndex"]
            content = self.get_chapter_info(c_id, p_index, l_location)
            print(content)
            time.sleep(5)


if __name__ == '__main__':
    DangDang("1901119271").run()

