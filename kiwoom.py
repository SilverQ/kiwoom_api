# https://www.youtube.com/watch?v=R5Vp4p5fjdc
import sys  # 파이썬 스크립트 관리 기능 포함
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *


class Kiwoom(QAxWidget):

    def __init__(self):
        # print('Kiwoom Start')
        super().__init__()
        self.login_event_loop = QEventLoop()  # 로그인을 요청하고 완료할 때까지 기다려주는 로프 변수
        self.calculator_event_loop = QEventLoop()  # 로그인을 요청하고 완료할 때까지 기다려주는 로프 변수
        self.get_ocx_instance()
        # 로그인을 하려면 알아야 하는 3가지 : 증권 서버에 요청하는 함수 '시그널', (이미 만들어져서 API로 제공)
        # 요청 결과를 어느 함수에서 받을지 지정해주는 '이벤트' (이미 만들어져서 API로 제공)
        # 요청 결과를 받을 함수인 '슬롯'
        self.event_slots()  # 이벤트 슬롯을 init 함수에서 실행
        self.signal_login_commConnect()  # 로그인 요청을 실행
        self.calculator_func()

    def get_ocx_instance(self):
        # OCX 방식으로 구성된 키움 관련 정보가 포함되어 있는 레지스트리 파일명 설정
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)

    def signal_login_commConnect(self):
        self.dynamicCall('CommConnect()')  # 로그인 요청 시그널
        self.login_event_loop.exec_()  # 이벤트 루프 실행

    def login_slot(self, err_code):
        if err_code == 0:
            print('Login Success')
        else:
            print('Error to Login')
        self.login_event_loop.exit()  # 직접 exit 함수로 종료시켜줘야 다음 코드가 실행

    def calculator_func(self):
        code_list = self.dynamicCall('GetCodeListByMarket(QString)', '0')
        code_list = code_list.split(';')[:-1]
        print('주식수: ', len(code_list), code_list[:10])  # 13503 000020;000 -> 1929개
        for idx, code in enumerate(code_list):
            code_nm = self.dynamicCall('GetMasterCodeName(QString)', code)
            print(f'{idx+1} / {len(code_list)} : {code} / {code_nm}')
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code):
        QTest.qWait(3600)  # 다음줄의 코드가 실행되는 것을 막으면서 요청 중인 이벤트 처리는 유지해주는 타이머 명령
        self.dynamicCall('SetInputValue(QString)', '종목코드', code)
        self.dynamicCall('SetInputValue(QString)', '수정주가구분', '1')
# https://youtu.be/SsPGK4rXq-E?t=204


class Main:

    def __init__(self):
        self.app = QApplication(sys.argv)  # 동시성 처리를 할 수 있게 해주는 함수를 포함
        self.kiwoom = Kiwoom()
        self.app.exec()  # 프로그램이 종료되지 않고 동시성 처리를 지원하도록 만들어줌


Main()
