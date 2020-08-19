
import time
import random
import urllib.request as request
import config
import json
import os


def GetTime(url):
    try:
        opener = request.build_opener()
        opener.addheaders = [('User-Agent', random.choice(headers))]
        post_json_text = json.loads(opener.open(url, timeout = 10).read().decode('utf-8'))
        created_at = post_json_text['data']['created_at']
        time_struct = time.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        time.sleep(2)
        if 'pics' in post_json_text['data']:
            pics = [term['url'] for term in post_json_text['data']['pics']]
            return created_at, pics
        return created_at, ''
    except Exception as e:
        print(e, url)
        time.sleep(30)




if __name__ == '__main__':
    root_url = 'https://m.weibo.cn/statuses/show?id='
    headers = config.getheaders()


    for root, dirs, files in os.walk('./data/'):
        for file in files:
            print(file)
            pics, flag = '', True
            if os.path.exists('./data_time/' + file[6:] + '_time'): continue
            with open('./data_time/' + file + '_time', 'wb') as f_time, open('./data/' + file, 'rb') as f_no_time:
                for line in f_no_time:
                    try:
                        if line.decode('utf-8')[:3] == 'id:':
                            f_time.write(line)
                            created_at, pics = GetTime(root_url + line.decode('utf-8').strip()[3:])
                            if pics: f_time.write(('pics:' + '****'.join(pics) + '\n').encode('utf-8'))
                            f_time.write(('created_at:' + created_at + '\n').encode('utf-8'))
                            pics, flag = '', True
                        elif line.decode('utf-8')[:11] == 'created_at:' and flag:
                            continue
                        elif line.decode('utf-8')[:5] == 'pics:':
                            pics = line
                        else:
                            f_time.write(line)
                    except:
                        if pics:  f_time.write(pics)
                        flag = False
                f_time.flush()



