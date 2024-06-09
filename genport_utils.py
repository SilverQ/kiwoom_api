import json
import telegram
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()
    options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
    options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함
    # options.add_argument("headless")  # 브라우저 백그라운드 실행

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def personal():
    with open("D:\DL_work\kiwoom_api\genport.json", "r") as chat_json:
        identification = json.load(chat_json)
        user_id = identification['id']
        user_pw = identification['pw']
    return user_id, user_pw


def send_msg(msg):
    with open("D:\DL_work\kiwoom_api\chatbot.json", "r") as chat_json:
        bot_token = json.load(chat_json)
        chat_id = bot_token['chat_id']
        bot = telegram.Bot(token=bot_token['token'])
        bot.sendMessage(chat_id=chat_id, text=msg)


