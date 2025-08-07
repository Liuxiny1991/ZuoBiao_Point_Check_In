
from tokenize import String
import requests
import re
import time
import os
from datetime import datetime


# --- 配置信息 ---
HOST = 'https://teamwork.cnhis.cc'
LOGIN_URI = f'{HOST}/teamworkapi/user/login'
GET_DOCUMENT_ID_URI = f'{HOST}/teamworkapi/api/ajax/inside/knowledge/getList'
DOCUMENT_RECORD_URI = f'{HOST}/process/dataDocument/documentRecord'
GET_INFO_URI = f'{HOST}/process/score/info'

# --- HTTP 请求头 ---

# 替代 notify 功能
def send(title, message):
    print(f"{title}: {message}")

# 获取环境变量 
def get_env(): 
    #判断 COOKIE_ZUOBIAO否存在于环境变量 
    if "ZUOBIAO" in os.environ: 
        # 读取系统变量以 \n 或 && 分割变量 
        cookie_list = os.environ.get('ZUOBIAO')
    else: 
        # 标准日志输出 
        print('❌未添加ZUOBIAO变量') 
        send('坐标自动刷积分', '❌未添加ZUOBIAO变量') 

        # 脚本退出 
        sys.exit(0) 

    return cookie_list 

# 其他代码...

class ZuoBiao:
    '''
    ZuoBiao类封装了签到、领取积分奖励的方法
    '''
    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data
        self.pageNum = os.environ.get('PageNum')
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://teamwork.cnhis.cc',
            'Sec-Ch-Ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
            'Host': 'teamwork.cnhis.cc',
            'Connection': 'keep-alive'
        }
    def getInfo_uri(self):
        return requests.get(GET_INFO_URI, self.headers).json()['data']['totalScore']


    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def set_document_record(self):
        '''
        写阅读记录
        '''
        print(self.headers['Content-Type'])
        self.headers['Content-Type']= 'application/json;charset=utf-8'
        for document in self.documents:
            param = {
              'documentId': document['id'],
              'type': '0'
            }
            response = requests.post(url=DOCUMENT_RECORD_URI, headers=self.headers, json=param).json()
            print(response)
            if response.get("data"):
                send('✅记录成功', f'文章标题：{document["title"]}')
            else:
                send('❌记录失败', f'文章标题：{document["title"]}')
            time.sleep(60) # 休眠60秒

    def get_document_id(self):
        '''
        获取文章
        :return: 返回所有文章
        '''
        param = {
            "pageNum": self.pageNum,
            "pageSize": 50,
            "secondarySort": 'createdTime',
        }
        #请求文章连接
        response = requests.post(url=GET_DOCUMENT_ID_URI, headers=self.headers, params=param).json()
        if response.get("map"):
            self.documents = response['map']['rows']
            self.set_document_record()
            return True, self.documents
        else:
            return False, response["message"]
    def do_login(self):
        """通过登录来刷新会话cookie"""
        print(f"正在为账号 [{self.param.get('account')}] 尝试登录并刷新Cookie...")
        self.headers.pop('Cookie', None)  # 移除旧的Cookie
        data = {'loginName': {self.param.get('account')}, 'password': self.param.get('password')}

        try:
            response = requests.post(LOGIN_URI, headers=self.headers, data=data)
            response.raise_for_status()  # 如果请求失败（如4xx或5xx错误），则抛出异常
            set_cookie_headers = response.headers.get('set-cookie')
            if set_cookie_headers:
                # 使用正则表达式从set-cookie头中提取SESSION和zb_sid
                session_match = re.search(r'SESSION=([^;,\s]+)', set_cookie_headers)
                zbsid_match = re.search(r'zb_sid=([^;,\s]+)', set_cookie_headers)

                if session_match and zbsid_match:
                    session_val = session_match.group(1)
                    zbsid_val = zbsid_match.group(1)
                    
                    my_cookie = f"SESSION={session_val}; zb_sid={zbsid_val}"
                    print(f'账号 [{self.param.get("account")}] 的Cookie刷新成功！')
                    print(f'新的Cookie为: {my_cookie}')
                    self.headers['Cookie'] = my_cookie
                    self.get_document_id() #开始获取帖子
                    return my_cookie
                else:
                    print(f"账号 [{self.param.get('account')}] 的Cookie解析失败，未找到SESSION或zb_sid。")
                    print(f"原始Set-Cookie头: {set_cookie_headers}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"账号 [{self.param.get('account')}] 刷新Cookie时出错: {e}")
        return None

def main():
    '''
    主函数
    :return: 返回一个字符串，包含积分结果
    '''
    msg = ""
    global cookie_zuobiao
    cookie_zuobiao = get_env()

    print("✅ 检测到共", len(cookie_zuobiao.get("ZUOBIAO")), "个坐标账号\n")

    i = 0
    for i in range(len(cookie_zuobiao.get("ZUOBIAO", []))):
        #print(i)
        _check_item = cookie_zuobiao.get("ZUOBIAO", [])[i]
        #print(_check_item)
         # 开始任务
        log = f"🙍🏻‍♂️ 第{i + 1}个账号"
        msg += log
        # 登录
        log = ZuoBiao(_check_item).do_login()
        msg += log + "\n"
        i += 1
    print(msg)

    try:
        send('坐标自动读帖子', msg)
    except Exception as err:
        print('%s\n❌ 错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------ZuoBiao开始刷积分----------")
    main()
    print("----------ZuoBiao刷积分完毕----------")
