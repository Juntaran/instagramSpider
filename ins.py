# coding=utf-8

'''
    Author: Juntaran
    Email:  Jacinthmail@gmail.com
    Date:   2018/9/24 01:36
'''

import requests
import time
import os
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json

# lantern
proxy_lantern = {
    "http": "http://127.0.0.1:59677",
    "https": "http://127.0.0.1:59677"
}

# shadowsocks
proxy_socks = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
}

header = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cookie': 'shbid=4419; rur=PRN; mcd=3; mid=W1E7cAALAAES6GY5Dyuvmzfbywic; csrftoken=uVspLzRYlxjToqSoTlf09JVaA9thPkD0; urlgen="{\"time\": 1532050288\054 \"2001:da8:e000:1618:e4b8:8a3d:8932:2621\": 23910\054 \"2001:da8:e000:1618:6c15:ccda:34b8:5dc8\": 23910}:1fgVTv:SfLAhpEZmvEcJn0037FXFMLJr0Y"',
    'referer': 'https://www.instagram.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

target = "sakumomo1203"

url_set = set([])  # set用来unique URL
pic_index = 0
url_set_size = 0
save_dir = './pic/' + target + '/'
pic_set = set()  # set用来unique URL


# 收集图片 url
def collect_pic_url(u_download):
    rec = requests.get(u_download, headers=header, proxies=proxy_socks)
    selector = etree.HTML(rec.content)

    w2json = selector.xpath('/html/body/script')[0].text
    w2json = w2json[w2json.find('=') + 1: -1]

    w = json.loads(w2json)
    pic_set.add(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_resources'][2]['src'])
    if 'edge_sidecar_to_children' in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']:
        for i in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            pic_set.add(i['node']['display_resources'][2]['src'])


# 下载图片
def download_pic():
    global pic_index
    print(len(pic_set))
    for i in pic_set:
        file_name = save_dir + target + "_" + str(pic_index) + i[-4:]
        pic_index += 1
        f = open(file_name, 'wb')
        pic_bin = requests.get(i, proxies=proxy_socks).content
        f.write(pic_bin)
        f.close()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    driver = webdriver.Chrome('/Users/juntaran/Downloads/chromedriver')
    raw_url = "https://www.instagram.com/" + target + "/"
    driver.get(raw_url)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    while (True):
        divs = driver.find_elements_by_class_name('v1Nh3')  # 这里最好使用xxxx_by_class_name，我尝试过用xpath绝对路径，但是好像对于页面变化比较敏感
        for u in divs:
            url_set.add(u.find_element_by_tag_name('a').get_attribute('href'))

        # 如果本次页面更新没有加入新的URL则可视为到达页面底端，跳出
        if len(url_set) == url_set_size:
            break

        url_set_size = len(url_set)

        # 三次滑动，保证页面足够更新
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)

    for url in url_set:
        collect_pic_url(url)

    download_pic()
