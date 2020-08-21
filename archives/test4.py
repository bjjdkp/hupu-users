# --*-- coding:utf-8 --*--
from neo4j import GraphDatabase

# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "942&op!UKVg2GQfL"))


def add_friend(tx, a_puid, b_puid):
    tx.run(
        "MERGE (a:User {puid:$a_puid, name:'张佳玮·信陵'})-[:follow]->(b:User{puid:$b_puid, name:'斌仔杰杰'})",
        a_puid=a_puid, b_puid=b_puid)

"""
PROFILE MERGE (a:User {puid: '5084612'})
        MERGE (a)-[:follow]-(b) return b
"""

def print_friends(tx, a_puid):
    b_list = tx.run("MATCH (a:User{puid:$puid})-[:follow]-(b) RETURN b",
                    puid=a_puid)
    print(len(list(b_list)))
    # for item in b_list:
    #     print(item["b"])


with GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "942&op!UKVg2GQfL")) as driver:
    with driver.session() as session:
        # session.write_transaction(add_friend, "Arthur", "Guinevere")
        # session.write_transaction(add_friend, "Arthur", "Lancelot")
        session.write_transaction(add_friend, "594", "18030641")
        # session.read_transaction(print_friends, "594")


# driver.close()

