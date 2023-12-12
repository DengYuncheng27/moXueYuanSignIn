import re
import pickle
from urllib.parse import unquote
import requests
import logging
from io import StringIO
from time import sleep
import telebot
from dotenv import load_dotenv
import os

'''
    魔学院自动签到脚本
    TODO:
        1. 日志规范化
        2. README
        3. BOT可选。推送规范化。  
        4. 推送时间可配置。  优先级低
'''

load_dotenv()  # 加载 .env 文件中的环境变量

uid = os.environ.get('USER_NAME')
pwd = os.environ.get('USER_PWD')
bot_open = os.environ.get('BOT_OPEN')
# bot config
if bot_open:
    BOT_TOKEN =  os.environ.get('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)
    chat_id = os.environ.get('BOT_CHAT_ID')

######### config  #########
login_url = 'https://api.moxueyuan.com/appapi.php/index?r=apiSystem/login'
signInUrl = 'https://api.moxueyuan.com/c45814c9a643ea71new3/appapi.php/index?r=apiSystem/sign'
token_cache_file = "token_cache.pkl"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Sec-Ch-Ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
login_payload = {
    'eid': 89981,
    'version': '6.0.0',
    'platform': 'pcweb',
    'language': 'zh_CN',
    'userPortallD': 0,
    'userNikkatsu': 45,
    'name': uid,
    'pwd': pwd,
    'complex': '1,2',
    'rulelds': 3,
}
signInPayload = {
    'eid': 89981,
    # 'token': token_value,
    # 'userid': uid_value,
    'version': '6.0.0',
    'platform': 'pcweb',
    'language': 'zh_CN',
    'userPortallD': 0,
    'userNikkatsu': 21,
    'randomListEncrypt': '',
}

# Set up logging

log_stream = StringIO()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# 创建一个文件处理器，指定输出到文件
file_handler = logging.FileHandler('sign_in.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

string_io_handler = logging.StreamHandler(log_stream)
string_io_handler.setLevel(logging.INFO)
# 创建日志格式器，可以自定义日志输出的格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 将格式器添加到处理器
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
string_io_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(string_io_handler)


def login_and_get_token(session):
    # 模拟登录请求
    response = session.post(login_url, data=login_payload, headers=headers)
    adminCookie = session.cookies.get('admin')
    decodeCookie = unquote(adminCookie)

    # 提取token和uid
    token_match = re.search(r's:5:"token";s:\d+:"(.*?)";', decodeCookie)
    uid_match = re.search(r's:3:"uid";s:\d+:"(.*?)";', decodeCookie)
    if token_match and uid_match:
        logger.info("登录成功！, 提取token")
        return token_match.group(1), uid_match.group(1)
    else:
        logger.error("登录失败或Token未找到!")
        exit(1)


def sign_in(session, signInPayload):
    '''
    签到
    :param signInPayload:
    :return:
    '''

    return session.post(signInUrl, data=signInPayload, headers=headers)


def do_sign_in_job():
    '''
        尝试登录脚本
    :return:
    '''
    # 初始化
    log_stream.truncate(0)
    session = requests.Session()
    # ... [其他设置代码，如headers, login_payload等]

    # 从缓存加载token和uid
    if os.path.exists(token_cache_file):
        with open(token_cache_file, 'rb') as file:
            token_value, uid_value = pickle.load(file)
            logger.debug("从缓存加载token和uid成功")
    else:
        token_value, uid_value = login_and_get_token(session)
        # 缓存token和uid
        with open(token_cache_file, 'wb') as file:
            pickle.dump((token_value, uid_value), file)
    signInPayload['token'] = token_value
    signInPayload['userid'] = uid_value
    response = sign_in(session, signInPayload)
    if response.status_code != 200:
        # 如果签到失败，尝试重新登录并签到
        logger.warning("签到失败，正在重新登录并尝试签到...")
        logger.warning("失败原因: %s %s", response.status_code, response.text)
        token_value, uid_value = login_and_get_token(session)
        # 更新缓存
        with open(token_cache_file, 'wb') as file:
            pickle.dump((token_value, uid_value), file)
        response = sign_in(session, signInPayload)

    # 重新输出签到结果
    if response.status_code == 200:
        logger.info("签到成功! %s %s", response.status_code, response.json().get("msg"))
    else:
        logger.error("签到失败: %s %s", response.status_code, response.text)


def get_logs():
    return log_stream.getvalue()


def schedule_job():
    do_sign_in_job()
    logs = get_logs()
    if bot_open:
        bot.send_message(chat_id=chat_id, text=logs)
        logger.info("bot has send message")


def check_job():
    """
        检查任务
    :return:
    """
    sleep(2) # wait 机器人加载~
    if(bot_open):
        logger.info("telegram bot open " )
    schedule_job()


if __name__ == '__main__':
    check_job()


