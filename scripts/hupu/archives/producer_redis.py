# --*-- coding:utf-8 --*--

import redis


class Task(object):
    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=0)
        self.pending_queue = 'hupu_users:neo_pending'

    def produce_task(self):
        for i in range(10, 20):

            self.rcon.lpush(self.pending_queue, i)

        # while True:
        #     task = self.rcon.blpop(self.queue, 0)[1]
        #     print("Task get", task)


if __name__ == '__main__':
    print('listen task queue')
    Task().produce_task()
