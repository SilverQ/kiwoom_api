import random
import time

import pandas as pd
import telegram
import json
import pyautogui as pag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# import pandas as pd
# 자동화 탐지 방지 : https://yoonminlee.com/selenium-bot-detection-bypass
from selenium.webdriver.chrome.options import Options

# 최신 버전의 크롬을 사용하기 위해 manager 활용
# https://srue.tistory.com/entry/%EC%98%A4%EB%A5%98-python-selenium-ChromeDriver
# 젠포트 최신 포트폴리오 크롤링해오기
# https://lyy9257.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%A4%91%EA%B8%89-1-%EC%A0%A0%ED%8F%AC%ED%8A%B8-%ED%8F%AC%ED%8A%B8%ED%8F%B4%EB%A6%AC%EC%98%A4-%EC%A2%85%EB%AA%A9-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%B4%EC%98%A4%EA%B8%B0


# 젠포트 오늘의 매수 종목 크롤링
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


def divider(l, n):
    for i in range(0, len(l), n):
        yield(l[i:i+n])


def get_table(dr, port_num='', tb_name='매수대상', tb_path=''):
    # 실전매매 포트 클릭
    # dr.find_element(By.XPATH, '//*[@id="list%s"]' %port_num).click()
    # dr.find_element(By.XPATH, tb_path).click()
    wait.until(EC.presence_of_element_located((By.XPATH, tb_path))).click()
    time.sleep(3+random.random())

    # 포트명 확인
    # element = dr.find_element(By.CLASS_NAME, 'port-tag-style-id')
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'port-tag-style-id')))
    port_id = element.text
    # print(port_id)
    element = dr.find_element(By.CLASS_NAME, 'port-name-over')
    port_name = element.text
    # print(port_name)
    time.sleep(3+random.random())

    # element = dr.find_element(By.XPATH, '//*[@id="tabMenu4"]')
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tabMenu4"]')))
    dr.execute_script('arguments[0].click();', element)
    time.sleep(2+random.random())
    # trade_lists = WebDriverWait(dr, 10).until(EC.presence_of_element_located(
    #     (By.XPATH, '//*[@id="PortManageSection4"]/div[3]/ul/table')
    # ))
    if tb_name=='매수대상':
        trade_lists = dr.find_elements(By.XPATH, '//*[@id="PortManageSection4"]/div[3]/ul/table')
    elif tb_name=='매도대상':
        trade_lists = dr.find_elements(By.XPATH, '//*[@id="PortManageSection4"]/div[4]/ul/table')

    # 추천종목: //*[@id="PortManageSection4"]/div[1]/ul
    # 보유종목: //*[@id="PortManageSection4"]/div[2]/ul
    # 매수대상: //*[@id="PortManageSection4"]/div[3]/ul
    time.sleep(1+random.random())

    temp = str('')

    for item in trade_lists:
        temp += item.text

    tr_list = list(divider(temp.split(), 6))
    col_list = tr_list[0]
    try:
        df = pd.DataFrame(tr_list[1:], columns=col_list)
    except Exception as e:
        df = None
    # print(random.random(), '\n', df)
    return port_id, port_name, df


def get_port_num(dr):
    tmp = dr.find_elements(By.CLASS_NAME, 'ui-sortable')
    print(tmp)
    temp = ''
    temp_id = ''
    temp_element = ''
    for item in tmp:
        temp += item.text
        temp_id += item.id
        temp_element += item.accessible_name
    # port_list = list(divider(temp.split(), 6))
    # col_list = tr_list[0]
    # df = pd.DataFrame(tr_list[1:], columns=col_list)
    tmp_dict = {}
    print('1. ', temp)
    print('2. ', temp_id)
    print('3. ', temp_element)
    return tmp_dict


dr = create_driver()
wait = WebDriverWait(dr, 10)

dr.get("http://intro.newsystock.com/login/")
dr.implicitly_wait(5)
# dr.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$loginID').send_keys(personal()[0])
wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$ContentPlaceHolder1$loginID'))).send_keys(personal()[0])
# dr.find_element(By.NAME, 'ctl00$ContentPlaceHolder1$loginPWD').send_keys(personal()[1])
wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$ContentPlaceHolder1$loginPWD'))).send_keys(personal()[1])
# time.sleep(1)
dr.implicitly_wait(3)
# dr.find_element(By.ID, 'ContentPlaceHolder1_btnLogin').click()
wait.until(EC.presence_of_element_located((By.ID, 'ContentPlaceHolder1_btnLogin'))).click()
time.sleep(5)
dr.implicitly_wait(4 + random.random())
# time.sleep(500)
dr.get('https://genport.newsystock.com/GenPro/PortManage.aspx')
time.sleep(5)
dr.implicitly_wait(5)

# port_dict = get_port_num(dr)
# port_dict = {}
# port_dict['AT4659525'] = '린다 라시케#1'
# port_dict['AT4659521'] = '피터린치 급성장#2'
port_xpath = ['/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[3]/div[4]/table/tbody/tr[1]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[3]/div[4]/table/tbody/tr[3]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[3]/div[4]/table/tbody/tr[5]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[3]/div[4]/table/tbody/tr[7]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[3]/div[4]/table/tbody/tr[9]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[5]/div[4]/table/tbody/tr[1]',
              '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[5]/div[4]/table/tbody/tr[3]']
# port_xpath = ['/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[5]/div[4]/table/tbody/tr[1]',
#               '/html/body/form/div[5]/div[10]/div[2]/div[3]/div[1]/div[5]/div[4]/table/tbody/tr[3]']

for k in port_xpath:
    msg_for_send = ''
    tmp_len1 = 0
    try:
        port_id, port_name, df = get_table(dr=dr, tb_path=k, tb_name='매수대상')
        # send_msg('포트: ' + port_id + ', ' + port_name)
        # send_msg('매수대상' + '\n' + df.to_string(index=False))
        # print(df)
        tmp_len1 += len(df)
    except Exception as e:
        # print(e)
        # print(tmp_len)
        pass
    msg_for_send += '포트: ' + port_id + ', ' + port_name
    if tmp_len1 > 0:
        msg_for_send += '\n' + '매수대상' + '\n' + df[['종목명', '종목코드', '매수가격(원)', '수량(주)']].to_string(index=False)
    else:
        msg_for_send += '\n' + '매수대상 없음'
        # send_msg('매수대상 없음')
    tmp_len2 = 0
    try:
        _, _, df = get_table(dr=dr, tb_path=k, tb_name='매도대상')
        # send_msg('포트명: ' + port_dict[k])
        # send_msg('매도대상' + '\n' + df.to_string(index=False))
        # print(df)
        tmp_len2 += len(df)
        # print(tmp_len)
    except Exception as e:
        # print(e)
        pass
    if tmp_len2 > 0:
        msg_for_send += 2 * '\n' + '매도대상' + '\n' + df[['종목명', '종목코드', '매도가격(원)', '수량(주)', '사유']].to_string(index=False)
    else:
        msg_for_send += '\n' + '매수대상 없음'
    # if tmp_len > 0:
    send_msg(msg_for_send)
print('done!')
# time.sleep(300)

# while True:
#     msg = 'Trading started'
#     print(time.time(), msg)
#     # bot.sendMessage(chat_id=chat_id, text="종목코드: {} , {}".format(code, event))
#     bot.sendMessage(chat_id=chat_id, text=msg)
#     pag.press('numlock')
#     time.sleep(1)
#     pag.press('numlock')
#     time.sleep(600)
