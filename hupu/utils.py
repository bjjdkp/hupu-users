# --*-- coding:utf-8 --*--

import string
import random
import hashlib


def get_sign(params_dict):
    sorted_dict = {key: params_dict[key] for key in sorted(params_dict)}
    params_str = '&'.join([key + '=' + str(sorted_dict[key]) for key in sorted_dict.keys()])
    params_str = params_str + 'HUPU_SALT_AKJfoiwer394Jeiow4u309'
    sign = hashlib.md5(params_str.encode()).hexdigest()
    return sign


def get_random_clientId():
    characters = string.digits
    return ''.join(random.choices(characters, k=8))


def get_random_ssid():
    characters = string.digits + string.ascii_letters
    return ''.join(random.choices(characters, k=15))+'='


def get_random_ssid_post():
    characters = string.digits + string.ascii_letters
    return ''.join(random.choices(characters, k=20))


def get_random_imei():
    # only in android
    digits = string.digits
    letters_digits = string.digits + string.ascii_lowercase
    str1 = ''.join(random.choices(digits, k=8))
    str2 = ''.join(random.choices(letters_digits, k=4))
    str3 = ''.join(random.choices(letters_digits, k=4))
    str4 = ''.join(random.choices(letters_digits, k=4))
    str5 = ''.join(random.choices(letters_digits, k=12))
    return '-'.join((str1, str2, str3, str4, str5))


def get_random_client():
    characters = string.digits + string.ascii_lowercase
    return ''.join(random.choices(characters, k=16))


def get_random_client_post():
    characters = string.digits + string.ascii_lowercase
    return ''.join(random.choices(characters, k=40))


if __name__ == '__main__':
    test = get_random_ssid()
    print(test)
