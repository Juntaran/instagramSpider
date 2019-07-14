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
import selenium.common
import json
import progressbar

driver = webdriver.Chrome('/Users/juntaran/Downloads/chromedriver')

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

target = "yua_mikami"

private = True

url_set = []
pic_set = []
pic_index = 0
url_set_size = 0
save_dir = './pic/' + target + '/'


# 收集图片 url
def collect_pic_url(u_download):
    print(u_download)

    if private:
        driver.get(u_download)
        rec = driver.page_source
        selector = etree.HTML(rec.content)
    else:
        rec = requests.get(u_download, headers=header, proxies=proxy_socks)
        selector = etree.HTML(rec)


    # 隐私账户需要登录

    # driver.get(u_download)
    # test = driver.page_source
    # print(test)
    #
    # rec = test


    # selector = etree.HTML(rec.content)
    # selector = etree.HTML(rec)

    w2json = selector.xpath('/html/body/script')[0].text
    w2json = w2json[w2json.find('=') + 1: -1]

    w = json.loads(w2json)
    print(w)
    pic_set.append(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_resources'][2]['src'])
    if 'edge_sidecar_to_children' in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']:
        for i in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            pic_set.append(i['node']['display_resources'][2]['src'])

    # 判断是否是视频
    if 'video_url' in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']:
        pic_set.append(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url'])


# 下载图片
def download_pic():
    global pic_index
    total = len(pic_set)
    print("The number of pictures waiting to be downloaded:", total)

    widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar('#'), ' ', progressbar.Timer(), ' ', progressbar.ETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=10*total).start()

    for i in range(total):
        file_name = save_dir + target + "_" + str(pic_index) + pic_set[i].split('?')[0][-4:]
        pic_index += 1
        f = open(file_name, 'wb')
        pic_bin = requests.get(pic_set[i], proxies=proxy_socks).content
        f.write(pic_bin)
        f.close()
        pbar.update(10 * i + 1)
    pbar.finish()


# 去重 list
def doList(list):
    temp = []
    for i in list:
        if i not in temp:
            temp.append(i)

    return temp


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    raw_url = "https://www.instagram.com/" + target + "/"
    driver.get(raw_url)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    count = 0
    sleeptime = 1.5

    # 这段时间输入用户名密码
    if private:
        time.sleep(60)
        driver.get(raw_url)

    while (True):
        # 这里最好使用xxxx_by_class_name，我尝试过用xpath绝对路径，但是好像对于页面变化比较敏感
        divs = driver.find_elements_by_class_name('v1Nh3')
        for u in divs:
            try:
                url_set.append(u.find_element_by_tag_name('a').get_attribute('href'))
            except selenium.common.exceptions.StaleElementReferenceException as ex:
                continue

        url_set = doList(url_set)

        # 如果本次页面更新没有加入新的URL则可视为到达页面底端，count+1,每次等待刷新时间 +1s
        if len(url_set) == url_set_size:
            count += 1
            sleeptime += 1
        else:
            count = 0
            sleeptime = 1

        # 如果连续 10 次都没有加入新 url，跳出
        if count == 10:
            print("Retry 3 times, I think there is no more pictures")
            break

        url_set_size = len(url_set)

        if count > 0:
            print("Retry %d times" % count)

        # 三次滑动，保证页面足够更新
        time.sleep(sleeptime)
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(sleeptime)
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(sleeptime)
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()

    # 对 url_set 去重
    url_set = doList(url_set)
    print("start collect picture url")
    total = len(url_set)
    print("The number of pictures waiting to be collected:", total)
    widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar('#'), ' ', progressbar.Timer(), ' ',
               progressbar.ETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=10 * total).start()

    for i in range(total):
        collect_pic_url(url_set[i])
        pbar.update(10 * i + 1)
    pbar.finish()

    # 对 pic_set 去重
    pic_set = doList(pic_set)
    download_pic()
