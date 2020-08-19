
import json
import GetIPProxy
import random
import config
import time
import urllib.request as request


def get_ip_prroxy_list():
    proxy_ip_list = GetIPProxy.get_proxy_ip()
    proxy_ip_list = [term[0] + ":" + str(term[1]) for term in proxy_ip_list]
    return proxy_ip_list


def getHtml(url, proxies):
    text = ''
    for i in range(1, 10):
        try:
            proxy = random.choice(proxies[0:20])
            proxy_support = request.ProxyHandler({"http": proxy})
            opener = request.build_opener(proxy_support)
            opener.addheaders = [('User-Agent', random.choice(headers))]
            text = opener.open(url, timeout = 30).read()
            return json.loads(text)
        except Exception as e:
            time.sleep(5)
            print(url, e, text)
            continue


def GetUserID(uid):
    start_url = 'http://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}'.format(uid = uid) #更新初始url
    depth, proxies = 0, get_ip_prroxy_list()

    while depth < 100:
        url = start_url + '&page=' + str(depth + 1)  # 翻页
        try:
            json_data = getHtml(url, proxies)
            if json_data['ok'] == 0: break
            card_list = json_data['data']['cards']
            for cards in card_list:
                if cards['card_type'] == 11:
                    card_groups = cards['card_group']
                    for term in card_groups:
                        uid = str(term['user']['id'])
                        uname = term['user']['screen_name']
                        print(uid, uname)
                        f_user_dict.write((uid + '||' + uname + '\n').encode('utf-8'))
                        user_dict2[uid] = uname
        except Exception as e:
            pass
        depth += 1



if __name__ == "__main__":
    headers = config.getheaders()


    user_dict1, user_dict2, user_get = {}, {}, {}
    before_id, now_id, flag = '', '', False
    for depth in range(0, 63):
        with open('./user_dict/user_dict' + str(depth), 'rb') as f_user_dict:
            for line in f_user_dict:
                uid, uname = line.decode('utf-8').strip().split('||')
                before_id, now_id = now_id, uid
                if depth == 61: flag = True

                if flag: user_dict1[uid] = uname
                else: user_get[uid] = uname
    print(len(user_dict1), len(user_get))

    depth = 63
    while depth < 100:
        with open('./user_dict/user_dict' + str(depth), 'wb') as f_user_dict:
            for uid, uname in user_dict1.items():
                if uid in user_get: continue
                user_get[uid] = uname
                if len(user_dict2) > 10000:
                    user_dict2[uid] = uname
                else:
                    GetUserID(uid)
        user_dict1, user_dict2 = user_dict2, {}
        depth += 1



