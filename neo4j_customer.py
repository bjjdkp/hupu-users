# --*-- coding:utf-8 --*--

import redis
import pickle
import logging
from hupu.settings import *
from py2neo import Graph

logging_level = logging.DEBUG

logging.basicConfig(
    level=logging_level,
    format="%(levelname)s %(asctime)s %(lineno)d: %(message)s"
)


class Neo4jCustomer(object):
    def __init__(self):
        self.redis_conn = redis.StrictRedis(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PARAMS["password"],
        )
        self.graph = Graph(NEO4J_URI, password=NEO4J_PWD)
        self.pending_queue = NEO4J_PENDING_QUEUE
        self.doing_queue = NEO4J_DOING_QUEUE

    def listen_task(self):
        todo_task = self.redis_conn.lpop(self.doing_queue)
        if todo_task:
            self.save_relationships(todo_task)

        while True:
            task = self.redis_conn.brpoplpush(
                self.pending_queue, self.doing_queue, 0
            )
            self.save_relationships(task)

    def save_relationships(self, task):
        self.graph.merge(pickle.loads(task))
        self.redis_conn.lpop(self.doing_queue)


if __name__ == '__main__':
    print('listen task queue...')
    Neo4jCustomer().listen_task()


