import json
import os
import re
import time
import GetIPProxy
import random
import requests
import config
from multiprocessing.dummy import Pool as ThreadPool


def get_ip_prroxy_list():
    proxy_ip_list = GetIPProxy.get_proxy_ip()
    proxy_ip_list = [term[0] + ":" + str(term[1]) for term in proxy_ip_list]
    return proxy_ip_list


def getHtml(url, proxies):
    for i in range(1, 10):
        try:
            text = requests.get(url, headers = {'User-Agent': random.choice(headers)}, proxies = {"http": random.choice(proxies[1:20])}).text
            return json.loads(text)
        except Exception as e:
            print(url, e)
            time.sleep(10)
            continue


def GetPostUrl(str_for_searching):
    url_original = "http://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{key_word}&page_type=searchall&page=".format(key_word=str_for_searching)
    proxies = get_ip_prroxy_list()
    with open('./data/'+ str_for_searching, 'wb') as fres:
        for page in range(1,6):
            try:
                url = url_original + str(page)
                json_data = getHtml(url, proxies)
                if json_data['ok'] == 0: return
                card_list = json_data['data']['cards']

                for card in card_list:
                    if card["card_type"] == 9:
                        bid = card['mblog']['id']
                        global post_id_get
                        if bid in post_id_get:
                            continue
                        else:
                            post_id_get = post_id_get.append(bid)
                        post_json_url = 'https://m.weibo.cn/statuses/show?id=' + bid
                        post_json_text = getHtml(post_json_url, proxies)
                        status_title = post_json_text['data']['status_title']
                        text = post_json_text['data']['text']
                        created_at = post_json_text['data']['created_at']

                        if re.match('\d+-\d+-\d+', created_at):  # 时间判断
                            e_time = time.mktime(time.strptime(created_at, "%Y-%m-%d"))
                            if e_time - s_time < 0: continue

                        if 'retweeted_status' in post_json_text['data']:
                            retweeted_status_bid = post_json_text['data']['retweeted_status']['bid']
                            retweeted_status_user_id = post_json_text['data']['retweeted_status']['user']['id']
                            fres.write(('retweeted_status_bid:' + str(retweeted_status_bid) + '\n').encode('utf-8'))
                            fres.write(('retweeted_status_user_id:' + str(retweeted_status_user_id) + '\n').encode('utf-8'))
                        time_struct = time.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
                        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
                        fres.write(('text:' + re.sub('<[^<]+?>', '', text) + '\n').encode('utf-8'))
                        time_struct = time.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
                        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
                        fres.write(('status_title:' + status_title + '\n').encode('utf-8'))
                        fres.write(('text:' + re.sub('<[^<]+?>', '', text) + '\n').encode('utf-8'))
                        fres.write(('created_at:' + created_at + '\n').encode('utf-8'))
            except Exception as e:
                print(e)

if __name__ == "__main__":
    s_time = time.mktime(time.strptime('2019-12-01', '%Y-%m-%d'))
    headers = config.getheaders()
    str_get, post_id_get = [], []

    for root, dirs, files in os.walk('./data/'):
        for file in files:
            str_get = str_get.append(file.strip())

    depth = 0
    tpool = ThreadPool(20)
    tpool.map(GetPostUrl, [str_for_searching for str_for_searching in str_get])