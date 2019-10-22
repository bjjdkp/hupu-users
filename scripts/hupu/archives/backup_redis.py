# --*-- coding:utf-8 --*--

# todo 根据redis内存占用，持久化数据
"""
1.固定时间段扫描请求队列hupu_users:requests长度
2.settings.py中，设置长度最大值，最小长度


3.超过最大值，将多余部分写入
4.低于最小值，数量补充道最小值

5.动态更换interval 浮动interval

"""

import time
import redis
from hupu.settings import *
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


class BackupRedis(object):

    def __init__(self):
        # self.maximum = PERSIST_MAXIMUM
        # self.minimum = PERSIST_MINIMUM
        self.maximum = 30
        self.minimum = 20

        self.redis_conn = redis.StrictRedis(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PARAMS["password"],
        )
        # self.requests_queue = "hupu_users:requests"
        self.requests_queue = "test"

        self.scheduler = BlockingScheduler()

        self.default_interval = 3

    def queue_counter(self):
        pipe = self.redis_conn.pipeline()
        pipe.multi()
        curr_count = self.redis_conn.zcard(self.requests_queue)

        if curr_count > self.maximum:
            # 保存少量
            pipe.zrange(self.requests_queue, self.maximum, curr_count)\
                .zremrangebyrank(self.requests_queue, self.maximum, curr_count)
            print(pipe.execute())
        elif curr_count < self.minimum:
            # 写入少量
            pass
            # print(pipe.zrange(self.requests_queue, self.maximum, curr_count))

    def test_add_queue(self):
        s_time = time.time()
        pipe = self.redis_conn.pipeline()
        pipe.multi()
        for i in range(50):
            pipe.zadd("test", {i: 1})
        pipe.execute()
        print("cost: %s" % (time.time()-s_time))

    def run(self):

        self.scheduler.add_job(
            self.queue_counter, 'interval', seconds=self.default_interval
        )

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass


if __name__ == '__main__':
    backup = BackupRedis()
    # backup.run()
    backup.test_add_queue()





