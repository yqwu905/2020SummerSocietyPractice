import requests
import json
import tkinter as tk
from bs4 import BeautifulSoup
import time
import warnings



warnings.filterwarnings('ignore')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 
             'Connection': 'keep-alive'}
long = 117.224817
latitude = 31.825842
distance = 6
num = 1596451211625


def getProxy():
    url = 'http://127.0.0.1:59977/getip?price=0&word=&count=10&type=json&detail=true'
    r = requests.get(url)
    proxys = json.loads(r.text)
    proxyList = []
    for i in proxys:
        print("IP:{}\tPort:{}\tOut IP:{}\tArea:{}".format(i['ip'], i['port'], i['out_ip'], i['area_text']))
        proxyList.append({'http':'http://{}:{}'.format(i['ip'], i['port'])})
    return proxyList

def loadCookie(fileName):
    cookie = requests.cookies.RequestsCookieJar()
    with open(fileName, 'r') as fp:
        data = json.load(fp)
    for i in data:
        cookie.set(i['name'], i['value'], domain=i['domain'], path=i['path'])
    return cookie

def getAllCompany(longtitude, latitude, distance, num):
    global cookie
    with open('{}-{}-{}-{}'.format(longtitude, latitude, distance, num), 'w') as fp:
        count = 0
        for page in range(1, 251):
            url = 'https://www.tianyancha.com/map/getListByPoint.html?pageNum={}&longtitude={}&latitude={}&distance={}&_={}'.format(page, longtitude, latitude, distance, num)
            while count < 5:
                try:
                    r = requests.get(url, cookies = cookie, headers = headers)
                    count = 0
                    break
                except:
                    print('Retry: {}/5'.format(count))
                    count += 1
            if count == 5:
                raise(Exception, "failed to connect")
            fp.write(r.text)
            if page < 250:
                fp.write('\n**********\n') 
            print('{}/250'.format(page))

def processHTML(fileName):
    with open(fileName, 'r') as fp:
        allHTML = fp.read()
    HTMLList = allHTML.split('**********')
    allCount = 0
    result = []
    for i in HTMLList:
        soup = BeautifulSoup(i, 'html.parser')
        tags = soup.find_all('td')
        value = []
        count = 0
        for j in tags:
            count += 1
            value.append(j.string)
            if count%8 == 0:
                allCount += 1
                #print(allCount, value)
                result.append({'name':value[1], 'regCurrent':value[3], 'regDate':value[4],\
                               'type':value[6], 'status':value[7]})
                value = []
    return result
                
def getCompanyByName(name):
    global cookie#, proxyList
    #proxy = proxyList[randint(0, len(proxyList) - 1)]
    url = 'https://www.tianyancha.com/search?key={}'.format(name)
    r = requests.get(url, cookies = cookie) #proxies = proxy)
    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.find_all('a')
    for i in tags:
        #print(i.string)
        if i.string == name:
            #print('find')
            print(i.get('href'))
            url = i.get('href')
            break
    r = requests.get(url, cookies = cookie)#, proxies = proxy)
    print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.find_all('span')#, class_ = 'sec-c3')
    for i in tags:
        print(i)
        
def getQCCCompanyByName(name):
    global qccCookie
    url = 'http://www.qcc.com/search?key={}'.format(name)
    r = requests.get(url, cookies = qccCookie, headers = headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.find_all('a')
    flag = False
    for i in tags:
        if i.get('href') != None:
            if '/firm/' in i.get('href') and '.shtml' in i.get('href'):
                url = 'https://www.qcc.com' + i.get('href')
                print('Find most closet result: {}'.format(url))
                flag = True
    if flag:
        r = requests.get(url, cookies = qccCookie, headers = headers)
        soup = BeautifulSoup(r.text)
        res = soup.find_all('span', class_ = 'ntag text-danger tooltip-br')
        print(res)
        res = res[0]
        spanTitle = BeautifulSoup(res.get('title'))
        res = spanTitle.find_all('span')
        data = {'date':'', 'reason':''}
        data['date'] = res[0].string[5:]
        data['reason'] = res[1].string[5:]
        return True, data
    else:
        return False, None
    
                

def ipTest():
    global proxyList
    for proxy in proxyList:
        print(proxy)
        r = requests.get('http://icanhazip.com', headers = headers, proxies = proxy)
        print(r.text)


if __name__ == '__main__':
    cookie = loadCookie('./cookie')
    qccCookie = loadCookie('./qcc_cookie')
    #proxyList = getProxy()
    #ipTest()
    #getAllCompany(117.224817, 31.825842, 6, 1596451211625)
    result = processHTML('117.224817-31.825842-6-1596451211625')
    with open('{}-{}-{}-{}-res'.format(long, latitude, distance, num), 'w') as fp:
        for i in result:
            if i['status'] == '注销':
                time.sleep(20)
                print(i)
                try:
                    flag, res = getQCCCompanyByName(i['name'])
                    if flag:
                        print(res)
                        fp.write('{},{},{},{},{},{},{}\n'.format(i['name'], i['regCurrent'], \
                            i['regDate'], i['type'], i['status'], res['date'], res['reason']))
                except:
                    pass
            
    #flag, res = getQCCCompanyByName('合肥梯递企业管理咨询有限公司')
    
    '''
    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.find_all('td')
    value = []
    count = 0
    for i in tags:
        count += 1
        value.append(i.string)
        if count%8 == 0:
            print(value)
            value = []
    '''