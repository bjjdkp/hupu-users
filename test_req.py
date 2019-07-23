# --*-- coding:utf-8 --*--

import json
import hashlib
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 5.1; Google Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 kanqiu/7.3.17.11347/7435 isp/1 network/WIFI",
}

params = {
    'puid': '34158589',
    'client': 'ce1057130688ebd2',
    'page': 2,
}


def get_sign(params_dict):
    sorted_dict = {key: params_dict[key] for key in sorted(params_dict)}
    params_str = '&'.join([key + '=' + str(sorted_dict[key]) for key in sorted_dict.keys()])
    params_str = params_str + 'HUPU_SALT_AKJfoiwer394Jeiow4u309'
    params_str_md5 = hashlib.md5(params_str.encode()).hexdigest()
    return params_str_md5

url = "https://bbs.mobileapi.hupu.com/1/7.3.17/user/getUserFollow"

# params["sign"] = get_sign(params)
res = requests.get(url, headers=headers, params=params).text

print(res)
print(bool(json.loads(res)["result"]["nextPage"]))



