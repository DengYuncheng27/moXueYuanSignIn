import datetime
import platform
from time import sleep

import pytz
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import telebot
import os

"""
# TODO 
    1. wait优化
"""

# config
load_dotenv()  # 加载 .env 文件中的环境变量

uid = os.environ.get('USER_NAME')
pwd = os.environ.get('USER_PWD')
bot_open = os.environ.get('BOT_OPEN', 0)
TOTAL_LIKE_NUM = 10  # 每次点赞数量
# bot config
print("env is ", uid, pwd, bot_open)

if bot_open:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)
    chat_id = os.environ.get('BOT_CHAT_ID')


import os

def list_files(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            print(os.path.join(root, name))


def main():
    # 检查操作系统
    if platform.system() == 'Windows':
        # Windows 系统
        geckodriver_path = "../drivers/geckodriver.exe"
    else:
        # Linux 或 macOS 系统
        geckodriver_path = "../drivers/geckodriver"  # 确保这个是 Linux/macOS 可执行版本的路径

    print("开始加载 geckodriver driver ... ", geckodriver_path)
    list_files('../drivers/')

    # 初始化 webdriver
    driver = webdriver.Firefox(service=Service(executable_path=geckodriver_path))

    driver.get("https://tuyoo.study.moxueyuan.com/new/login")
    try:
        user_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='账号']"))
        )
        pwd_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码']"))
        )
        user_input.clear()
        user_input.send_keys(uid)
        pwd_input.clear()
        pwd_input.send_keys(pwd)
        button = driver.find_element(By.CLASS_NAME, "loginProBtn")
        button.click()
        sign_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "signInBtn"))
        )
        sign_button.click()
        bot_send_message("签到成功")
        # 跳转到社区
        print("跳转到社区")

        community_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='app']/div/header/div[2]/div[2]/div/div[2]/div/div[3]/div/div/div[1]"))
        )
        community_btn.click()
        cur_like_count = 0
        while cur_like_count < TOTAL_LIKE_NUM:
            cur_page_loc = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".number.active"))
            )
            print("cur page is ", cur_page_loc.text)
            sleep(2)  # 等等下面这个icons

            try:
                icons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".giveUp-icon.mr4")))

                good_btns = [icon.find_element(By.XPATH, '..') for icon in icons]
                print("total can operate like", len(good_btns))
                wait = WebDriverWait(driver, 10)  # 等待最多10秒
                for btn in good_btns:
                    wait.until(EC.element_to_be_clickable(btn))
                    sleep(1)  # 1s 点 1次 主要向btn上面的遮盖罩妥协了
                    html = btn.get_attribute('outerHTML')
                    btn.click()
                    cur_like_count += 1
                    if cur_like_count >= TOTAL_LIKE_NUM:
                        print(" task end , total like ", cur_like_count)
                        exit()
            except TimeoutException:
                print(TimeoutException)
            finally:
                navi_btn = driver.find_element(By.XPATH, f"//li[contains(text(),'{int(cur_page_loc.text) + 1}')]")
                navi_btn.click()
                bot_send_message(f"完成点赞任务, total like {cur_like_count}")
    finally:
        driver.quit()


def bot_send_message(message):
    # 获取当前时间
    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

    # 格式化时间
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 拼接字符串
    message = f'{time_str} - seleminun impl {message}'

    # 发送消息
    if bot_open:
        bot.send_message(chat_id=chat_id, text=message)


main()
