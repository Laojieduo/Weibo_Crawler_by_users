
import json
import os
import re
import time
import GetIPProxy
import random
import urllib.request as request
import config
import datetime
from multiprocessing.dummy import Pool as ThreadPool


def get_ip_prroxy_list():
    proxy_ip_list = GetIPProxy.get_proxy_ip()
    proxy_ip_list = [term[0] + ":" + str(term[1]) for term in proxy_ip_list]
    return proxy_ip_list


def getHtml(url, proxies):
    for i in range(1):
        try:
            print(url)
            opener = request.build_opener()
            opener.addheaders = [('User-Agent', random.choice(headers))]
            text = json.loads(opener.open(url, timeout = 10).read())
            time.sleep(2)
            return text
        except Exception as e:
            print(url, e)
            time.sleep(30)



def conv_time(t):
    min = re.findall('\d+', t)[0]
    if u'分钟' in t:
        c = time.time() - int(min) * 60
        return time.strftime('%Y-%m-%d', time.localtime(c))

    elif u'小时' in t:
        c = time.time() - int(min) * 60 * 60
        return time.strftime('%Y-%m-%d', time.localtime(c))

    elif u'天' in t:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        return str(yesterday)
    elif len(t) == 5:
        return '2020-' + t
    else:
        return t



def GetPostUrl(x):
    uid, uname = x[0], x[1]
    if uid in user_get: return

    print(x)
    user_get[uid] = uname
    start_url = 'http://m.weibo.cn/api/container/getIndex?containerid=230413{uid}_-_WEIBO_SECOND_PROFILE_WEIBO'.format(uid = uid) #更新初始url
    depth, flag_zhiding = 0, False  # 需要判断是否置顶
    with open('./data/'+ uid + '_' + uname, 'wb') as fres:
        while True:
            proxies = get_ip_prroxy_list()
            try:
                url = start_url + '&page=' + str(depth + 1)  #翻页
                json_data = getHtml(url, proxies)
                card_list = json_data['data']['cards']
                if json_data['ok'] == 0: return
                if len(card_list) == 1 and card_list[0]['card_type'] == 58: return

                for cards in card_list:
                    if cards['card_type'] == 9:
                        created_at = conv_time(cards['mblog']['created_at'])
                        reposts_count = cards['mblog']['reposts_count']     # 转发量
                        attitudes_count = cards['mblog']['attitudes_count'] # 点赞数
                        comments_count = cards['mblog']['comments_count']   # 评论数
                        id = cards['mblog']['id']
                        isLongText = cards['mblog']['isLongText']
                        text = cards['mblog']['text']

                        e_time = time.mktime(time.strptime(created_at, "%Y-%m-%d"))
                        if e_time - s_time < 0 and flag_zhiding: return
                        if e_time - s_time < 0: flag_zhiding = True


                        if isLongText:
                            try:
                                post_json_url = 'https://m.weibo.cn/statuses/extend?id=' + id
                                post_json_text = getHtml(post_json_url, proxies)
                                text = post_json_text['data']['longTextContent']
                            except Exception as e:
                                print(e)


                        if 'retweeted_status' in cards['mblog']:
                            retweeted_status_id = cards['mblog']['retweeted_status']['id']
                            retweeted_status_user_id = cards['mblog']['retweeted_status']['user']['id']
                            fres.write(('retweeted_status_id:' + str(retweeted_status_id) + '\n').encode('utf-8'))
                            fres.write(('retweeted_status_user_id:' + str(retweeted_status_user_id) + '\n').encode('utf-8'))


                        if 'pics' in cards['mblog']:
                            pics = [term['url'] for term in cards['mblog']['pics']]
                            fres.write(('pics:' + '****'.join(pics) + '\n').encode('utf-8'))


                        fres.write(('id:' + id + '\n').encode('utf-8'))
                        fres.write(('text:' + re.sub('<[^<]+?>', '', text) + '\n').encode('utf-8'))
                        fres.write(('created_at:' + created_at + '\n').encode('utf-8'))
                        fres.write(('reposts_count:' + str(reposts_count) + '\n').encode('utf-8'))
                        fres.write(('attitudes_count:' + str(attitudes_count) + '\n').encode('utf-8'))
                        fres.write(('comments_count:' + str(comments_count) + '\n\n').encode('utf-8'))
                        fres.flush()
            except Exception as e:
                print(e)
            depth += 1



if __name__ == "__main__":
    s_time = time.mktime(time.strptime('2020-01-01', '%Y-%m-%d'))
    headers = config.getheaders()
    user_dict, user_get = {}, {}

    for root, dirs, files in os.walk('./data/'):
        for file in files:
            uid,uname = file.strip().split('_', 1)
            user_get[uid] = uname


    with open('./user_dict' + str(1), 'rb') as f_user_dict:
        for line in f_user_dict:
            uid, uname = line.decode('utf-8').strip().split('||')
            user_dict[uid] = uname
        tpool = ThreadPool(1)
        tpool.map(GetPostUrl, user_dict.items())




