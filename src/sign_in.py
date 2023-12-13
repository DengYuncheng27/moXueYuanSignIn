from time import sleep

from selenium import webdriver
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
# bot config
print("env is ", uid, pwd, bot_open)
if bot_open:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)
    chat_id = os.environ.get('BOT_CHAT_ID')

driver = webdriver.Firefox(service=Service(executable_path="../drivers/geckodriver.exe"))
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
    sleep(20)
finally:
    driver.quit()

