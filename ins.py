# coding=utf-8

'''
    Author: Juntaran
    Email:  Jacinthmail@gmail.com
    Date:   2018/9/24 01:36
'''

import requests
import time
import os
import re
import hashlib
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common
import progressbar

"""
    http://npm.taobao.org/mirrors/chromedriver/
"""

private = True

driver = webdriver.Chrome('/Users/juntaran/Downloads/chromedriver')

# lantern
proxy_lantern = {
    "http": "http://127.0.0.1:59677",
    "https": "http://127.0.0.1:59677"
}

shadowsocks = "127.0.0.1:1080"

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




def read_config():
    target_list = []
    with open("links.txt", 'r', encoding='utf-8') as f:
        for line in f:
            target_list.extend(line.split(' '))
    return target_list


# 收集图片 url
def collect_pic_url(u_download):
    pic_set = []

    if private:
        # 隐私账户需要登录
        driver.get(u_download)
        rec = driver.page_source
        selector = etree.HTML(rec)
    else:
        rec = requests.get(u_download, headers=header, proxies=proxy_socks, timeout=10)
        selector = etree.HTML(rec.content)

    if len(selector.xpath('/html/body/script')) > 11:
        w2json = selector.xpath('/html/body/script')[11].text
        w2json = w2json[w2json.find(',') + 1: -2]

        # start = w2json.find('display_url') + 14
        for each in re.finditer('display_url', w2json):
            start = each.start() + 14
            end = start
            for ch in w2json[start:]:
                if ch == '\"':
                    break
                end += 1

            tmp_url = w2json[start: end]
            pic_url = tmp_url.replace("\\u0026", "&")
            print(pic_url)
            pic_set.append(pic_url)

        # find video
        for each in re.finditer('video_url', w2json):
            start = each.start() + 12
            end = start
            for ch in w2json[start:]:
                if ch == '\"':
                    break
                end += 1

            tmp_url = w2json[start: end]
            pic_url = tmp_url.replace("\\u0026", "&")
            print(pic_url)
            pic_set.append(pic_url)

        # 对 pic_set 去重
        pic_set = doList(pic_set)
        if not download_pic(save_dir, target, pic_set, pic_index, md5_set):
            return False
    else:
        print("error page:", u_download)

    return True

    # w = json.loads(w2json)
    # print(w)
    # pic_set.append(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_resources'][2]['src'])
    # if 'edge_sidecar_to_children' in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']:
    #     for i in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
    #         pic_set.append(i['node']['display_resources'][2]['src'])
    #         print(i['node']['display_resources'][2]['src'])
    #
    # # 判断是否是视频
    # if 'video_url' in w['entry_data']['PostPage'][0]['graphql']['shortcode_media']:
    #     pic_set.append(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url'])
    #     print(w['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url'])


# 下载图片
def download_pic(save_dir, target, pic_set, pic_index, md5_set):
    total = len(pic_set)
    print(pic_set)
    print("The number of pictures waiting to be downloaded:", total)

    for i in range(total):
        # file_name = save_dir + target + "_" + str(pic_index) + pic_set[i].split('?')[0][-4:]
        print(pic_set[i])
        t = time.time()
        file_name = save_dir + target + "_" + str(int(round(t * 1000))) + ".jpg"
        if '.mp4' in pic_set[i]:
            file_name = save_dir + target + "_" + str(int(round(t * 1000))) + ".mp4"

        tmp_file_name = file_name + "_tmp"
        pic_index += 1

        f = open(tmp_file_name, 'wb')
        pic_bin = requests.get(pic_set[i], proxies=proxy_socks).content
        f.write(pic_bin)
        f.close()

        tmp_md5 = cal_file_md5(tmp_file_name)
        if tmp_md5 in md5_set:
            os.remove(tmp_file_name)
            return False
        else:
            os.rename(tmp_file_name, file_name)

    return True


# 去重 list
def doList(list):
    temp = []
    for i in list:
        if i not in temp:
            temp.append(i)

    return temp


# 计算文件 MD5
def cal_file_md5(file_name):
    if not os.path.isfile(file_name):
        return None

    f_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        f_md5.update(f.read())
        _hash = f_md5.hexdigest()
        return str(_hash).upper()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('--proxy-server=%s' % shadowsocks)

    target_list = read_config()

    # driver = webdriver.Chrome(options=options)

    ins = "https://www.instagram.com"
    driver.get(ins)

    count = 0
    sleeptime = 1.5

    # 这段时间输入用户名密码
    # if private:
    time.sleep(30)

    for target in target_list:
        target = target.replace("\n", "")
        raw_url = "https://www.instagram.com/" + target + "/"
        save_dir = './pic/' + target + '/'

        md5_set = []
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        else:
            file_list = os.listdir(save_dir)
            for i in file_list:
                each_file_path = save_dir + '/' + i
                md5_set.append(cal_file_md5(each_file_path))

        driver.get(raw_url)

        url_set = []
        url_set_size = 0

        pic_set = []
        pic_index = 0

        while True:
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

            # 如果连续 3 次都没有加入新 url，跳出
            if count == 7:
                print("Retry %s times, I think there is no more pictures" % count)
                break

            url_set_size = len(url_set)

            if count > 0:
                print("Retry %d times" % count)

            # 3 次滑动，保证页面足够更新
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
            print(i)
            if not collect_pic_url(url_set[i]):
                break
            else:
                pbar.update(10 * i + 1)
        pbar.finish()


# coding=utf-8

'''
    Author: Juntaran
    Email:  Jacinthmail@gmail.com
    Date:   2018/9/24 01:36
'''

import requests
import time
import os
import re
import hashlib
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common
import progressbar

"""
    http://npm.taobao.org/mirrors/chromedriver/
"""

private = True

driver = webdriver.Chrome('/Users/juntaran/Downloads/chromedriver')

# lantern
proxy_lantern = {
    "http": "http://127.0.0.1:59677",
    "https": "http://127.0.0.1:59677"
}

shadowsocks = "127.0.0.1:1080"

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


def read_config():
    target_list = []
    with open("links.txt", 'r', encoding='utf-8') as f:
        for line in f:
            target_list.extend(line.split(' '))
    return target_list


# 收集图片 url
def collect_pic_url(u_download):
    pic_set = []

    if private:
        # 隐私账户需要登录
        driver.get(u_download)
        rec = driver.page_source
        selector = etree.HTML(rec)
    else:
        rec = requests.get(u_download, headers=header, proxies=proxy_socks, timeout=10)
        selector = etree.HTML(rec.content)

    if len(selector.xpath('/html/body/script')) > 11:
        w2json = selector.xpath('/html/body/script')[11].text
        w2json = w2json[w2json.find(',') + 1: -2]

        # start = w2json.find('display_url') + 14
        for each in re.finditer('display_url', w2json):
            start = each.start() + 14
            end = start
            for ch in w2json[start:]:
                if ch == '\"':
                    break
                end += 1

            tmp_url = w2json[start: end]
            pic_url = tmp_url.replace("\\u0026", "&")
            print(pic_url)
            pic_set.append(pic_url)

        # find video
        for each in re.finditer('video_url', w2json):
            start = each.start() + 12
            end = start
            for ch in w2json[start:]:
                if ch == '\"':
                    break
                end += 1

            tmp_url = w2json[start: end]
            pic_url = tmp_url.replace("\\u0026", "&")
            print(pic_url)
            pic_set.append(pic_url)

        # 对 pic_set 去重
        pic_set = doList(pic_set)
        if not download_pic(save_dir, target, pic_set, pic_index, md5_set):
            return False
    else:
        print("error page:", u_download)

    return True


# 下载图片
def download_pic(save_dir, target, pic_set, pic_index, md5_set):
    total = len(pic_set)
    print(pic_set)
    print("The number of pictures waiting to be downloaded:", total)

    for i in range(total):
        # file_name = save_dir + target + "_" + str(pic_index) + pic_set[i].split('?')[0][-4:]
        print(pic_set[i])
        t = time.time()
        file_name = save_dir + target + "_" + str(int(round(t * 1000))) + ".jpg"
        if '.mp4' in pic_set[i]:
            file_name = save_dir + target + "_" + str(int(round(t * 1000))) + ".mp4"

        tmp_file_name = file_name + "_tmp"
        pic_index += 1

        f = open(tmp_file_name, 'wb')
        pic_bin = requests.get(pic_set[i], proxies=proxy_socks).content
        f.write(pic_bin)
        f.close()

        tmp_md5 = cal_file_md5(tmp_file_name)
        if tmp_md5 in md5_set:
            os.remove(tmp_file_name)
            return False
        else:
            os.rename(tmp_file_name, file_name)

    return True


# 去重 list
def doList(list):
    temp = []
    for i in list:
        if i not in temp:
            temp.append(i)

    return temp


# 计算文件 MD5
def cal_file_md5(file_name):
    if not os.path.isfile(file_name):
        return None

    f_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        f_md5.update(f.read())
        _hash = f_md5.hexdigest()
        return str(_hash).upper()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('--proxy-server=%s' % shadowsocks)

    target_list = read_config()

    # driver = webdriver.Chrome(options=options)

    ins = "https://www.instagram.com"
    driver.get(ins)

    count = 0
    sleeptime = 1.5

    # 这段时间输入用户名密码
    # if private:
    time.sleep(30)

    for target in target_list:
        target = target.replace("\n", "")
        raw_url = "https://www.instagram.com/" + target + "/"
        save_dir = './pic/' + target + '/'

        md5_set = []
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        else:
            file_list = os.listdir(save_dir)
            for i in file_list:
                each_file_path = save_dir + '/' + i
                md5_set.append(cal_file_md5(each_file_path))

        driver.get(raw_url)

        url_set = []
        url_set_size = 0

        pic_set = []
        pic_index = 0

        while True:
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

            # 如果连续 count 次都没有加入新 url，跳出
            if count == 7:
                print("Retry %s times, I think there is no more pictures" % count)
                break

            url_set_size = len(url_set)

            if count > 0:
                print("Retry %d times" % count)

            # 3 次滑动，保证页面足够更新
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
            print(i)
            if not collect_pic_url(url_set[i]):
                break
            else:
                pbar.update(10 * i + 1)
        pbar.finish()


