from PyQt5 import uic
from Kiwoom import *
from pywinauto import application
from pywinauto import timings
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import telegram

# 파이썬으로 배우는 알고리즘 트레이딩(메인)
# https://wikidocs.net/5859
# 파이썬으로 텔레그램 봇 사용하기
# https://kminito.tistory.com/37?category=373099

# Qt-desiner
# https://build-system.fman.io/qt-designer-download

form_class = uic.loadUiType("pytrader1.ui")[0]


class MyWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.kiwoom = Kiwoom()
        self.initUI()
        self.kiwoom.comm_connect()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.timer = QTimer(self)
        self.timer.start(500)
        self.timer.timeout.connect(self.timeout)

        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox.addItems(accounts_list)

        self.lineEdit.textChanged.connect(self.code_changed)  # 종목 항목에 코드 입력시
        self.pushButton.clicked.connect(self.send_order)  # 현금 주문 클릭시

        self.load_condition_list()  # 시작할 때 리스트를 채워준다
        self.checkBox_cond.setChecked(False)  # 체크박스 체크를 기본 설정으로
        self.pushButton_cond.clicked.connect(self.start_cond)

    def initUI(self):
        self.setWindowTitle('Condition Monitor Bot v0.1')
        self.move(100, 100)

    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)
        cur_val = self.kiwoom.get_current_code_value(code)
        # print('현재가: ', cur_val)
        self.spinBox_2.setValue(cur_val)
        # try:
        #     cur_val = self.kiwoom.get_current_code_value(code)
        #     print('현재가: ', cur_val)
        #     self.spinBox_2.setValue(cur_val)
        # except Exception as e:
        #     print('error: ', e)
        #     # pass

    def send_order(self):
        print('주문: ', self.lineEdit.text())
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        self.kiwoom.send_order("send_order_req", "0101",
                               account, order_type_lookup[order_type],
                               code, num, price, hoga_lookup[hoga], "")

    def timeout(self):
        current_time = QTime.currentTime()
        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)
        if self.kiwoom.msg:
            try:
                # 텔레그램
                if self.checkBox_cond.isChecked():
                    self.kiwoom.bot.sendMessage(chat_id=self.kiwoom.chat_id, text=self.kiwoom.msg)
            except Exception as e:
                print('Telegram Message Error: ', e)
            try:
                # 로그창에 내용 입력
                self.textEdit_cond.append(self.kiwoom.msg)
                self.kiwoom.msg = ""
            except:
                pass

    """ condiComboBox에 condition List를 설정 """
    def load_condition_list(self):
        print("pytrader.py [load_condition_list]")

        cond_list = []
        try:
            # 조건식 실행
            self.kiwoom.getConditionLoad()
            # getConditionLoad 가 정상 실행되면 kiwoom.condition에 조건식 목록이 들어간다.
            dic = self.kiwoom.condition

            for key in dic.keys():
                cond_list.append("{};{}".format(key, dic[key]))

            # 콤보박스에 조건식 목록 추가
            self.comboBox_cond.addItems(cond_list)

        except Exception as e:
            print(e)
        # return dic  # 내가 추가한 코드, 반환된 리스트를 채팅으로 보내려면?

    def start_cond(self):
        conditionIndex = self.comboBox_cond.currentText().split(';')[0]
        conditionName = self.comboBox_cond.currentText().split(';')[1]

        if self.pushButton_cond.text() == "적용":
            try:
                print('조건검색 조회')
                self.kiwoom.sendCondition("0", conditionName, int(conditionIndex), 1)
                self.pushButton_cond.setText("해제")
                self.comboBox_cond.setEnabled(False)
                self.checkBox_cond.setEnabled(False)
                print("{} activated".format(conditionName))

            except Exception as e:
                print('here?', e)  # 'Kiwoom' object has no attribute 'comboBox_cond'

        else:
            self.kiwoom.sendConditionStop("0", conditionName, conditionIndex)
            self.pushButton_cond.setText("적용")
            self.comboBox_cond.setEnabled(True)
            self.checkBox_cond.setEnabled(True)


def auto_update():
    app = application.Application()
    app.start("C:/OpenAPI/opversionup.exe")

    title = "업그레이드 확인"
    dlg = timings.WaitUntilPasses(10, 0.5, lambda: app.window_(title=title))

    btn_ctrl = dlg.Button0
    btn_ctrl.Click()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auto_update()
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
