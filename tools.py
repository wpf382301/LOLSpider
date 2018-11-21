import os
import re

import requests
from requests import RequestException


def make_local_dir(url, save_dir, name):
    if ".jpg" in url:
        gs = "jpg"
    else:
        gs = "png"
    file_path = '{0}\\{1}.{2}'.format(save_dir, name, gs)
    return file_path


def check_name_valid(name=None):
    if name is None:
        print("name is None!")
        return
    reg = re.compile(r'[\\/:*?"<>|\r\n]+')
    valid_name = reg.findall(str(name))
    if valid_name:
        for nv in valid_name:
            name = name.replace(nv, "-")
    return name


def download_img(url, save_dir, name):
    url = check_url_schema(url)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = make_local_dir(url, save_dir, name)
    if not os.path.exists(file_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('Download image: {} failed\nerror code: {}'.format(url, response.status_code))
        except RequestException as e:
            print(e)
            print('Download image error, retrying...')
            return download_img(url, save_dir, name)


def check_url_schema(url):
    if url.startswith("//"):
        return "http:" + url
    else:
        return url
