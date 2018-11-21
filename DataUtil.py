import requests
import re
import json


def get_heroes_info():
    response = requests.get('http://gpcd.gtimg.cn/upload/qqtalk/lol_hero/1d/hero_list.js')
    if response.status_code == 200:
        return response.json()
    return None


def get_hero_detail(hero_id):
    response = requests.get('http://gpcd.gtimg.cn/upload/qqtalk/lol_hero/1d/hero_{}.js'.format(hero_id))
    if response.status_code == 200:
        return response.json()
    return None


def get_goods_info():
    response = requests.get('http://gpcd.gtimg.cn/upload/qqtalk/lol_hero/1d/goods_list.js')
    if response.status_code == 200:
        return response.json()['items']
    return None


def get_good_detail(good_id):
    response = requests.get('http://gpcd.gtimg.cn/upload/qqtalk/lol_hero/1d/good_{}.js'.format(good_id))
    if response.status_code == 200:
        return response.json()
    return None


def get_skins_info():
    response = requests.get('http://lol.qq.com/biz/hero/skins.js')
    if response.status_code == 200:
        a = re.compile('skins=(.*?);', re.S).search(response.text)
        return json.loads(a.group(1))['data']
    return None
