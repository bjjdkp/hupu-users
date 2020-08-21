# --*-- coding:utf-8 --*--
import csv
from collections import Counter

user_id_list = []


with open('users.csv') as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    for row in f_csv:
        user_id_list.append(int(row[0]))

res = Counter(user_id_list)
print(res.most_common(50))








