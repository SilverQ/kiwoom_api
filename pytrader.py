from PyQt5 import uic
from Kiwoom import *
from pywinauto import application
from pywinauto import timings
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
from multiprocessing import Queue
import telegram

# 파이썬으로 배우는 알고리즘 트레이딩(메인)
# https://wikidocs.net/5859
# 파이썬으로 텔레그램 봇 사용하기
# https://kminito.tistory.com/37?category=373099

# Qt-desiner
# https://build-system.fman.io/qt-designer-download

form_class = uic.loadUiType("pytrader1.ui")[0]


# 실시간으로 들어오는 데이터를 보고 주문 여부를 판단하는 스레드
class Worker(QThread):
    # argument는 없는 단순 trigger
    # 데이터는 queue를 통해서 전달됨
    trigger = pyqtSignal()

    def __init__(self, data_queue, order_queue):
        super().__init__()
        self.data_queue = data_queue                # 데이터를 받는 용
        self.order_queue = order_queue              # 주문 요청용
        self.timestamp = None
        self.limit_delta = datetime.timedelta(seconds=2)

    def run(self):
        while True:
            if not self.data_queue.empty():
                data = self.data_queue.get()
                result = self.process_data(data)
                if result:
                    self.order_queue.put(data)                      # 주문 Queue에 주문을 넣음
                    self.timestamp = datetime.datetime.now()        # 이전 주문 시간을 기록함
                    self.trigger.emit()

    def process_data(self, data):
        # 시간 제한을 충족하는가?
        time_meet = False
        if self.timestamp is None:
            time_meet = True
        else:
            now = datetime.datetime.now()                           # 현재시간
            delta = now - self.timestamp                            # 현재시간 - 이전 주문 시간
            if delta >= self.limit_delta:
                time_meet = True

        # 알고리즘을 충족하는가?
        algo_meet = False
        if data % 2 == 0:
            algo_meet = True

        # 알고리즘과 주문 가능 시간 조건을 모두 만족하면
        if time_meet and algo_meet:
            return True
        else:
            return False


class MyWindow(QMainWindow, form_class):

    def __init__(self, data_queue, order_queue):
        super().__init__()
        self.setupUi(self)

        self.kiwoom = Kiwoom()
        self.initUI()
        self.kiwoom.comm_connect()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.data_queue = data_queue
        self.order_queue = order_queue

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
        # self.check_box_receive_msg.setChecked(False)  # 체크박스 체크를 기본 설정으로
        self.pushButton_cond.clicked.connect(self.search_cond)
        searched_codes = self.search_cond()
        # self.timer.start(5000)
        # self.auto_send_order(searched_codes)

        # thread start
        self.worker = Worker(data_queue, order_queue)
        self.worker.trigger.connect(self.pop_order)
        self.worker.start()

        # 데이터가 들어오는 속도는 주문보다 빠름
        self.timer1 = QTimer()
        self.timer1.start(1000)
        self.timer1.timeout.connect(self.push_data)

    def push_data(self):
        now = datetime.datetime.now()
        self.data_queue.put(now.second)

    @pyqtSlot()
    def pop_order(self):
        if not self.order_queue.empty():
            data = self.order_queue.get()
            print(data)

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

    def get_val(self, code):
        name = self.kiwoom.get_master_code_name(code)
        cur_val = self.kiwoom.get_current_code_value(code)
        return [name, cur_val]

    def auto_send_order(self, searched_codes):
        for code in searched_codes:
            name, cur_val = self.get_val(code)
            self.send_order2(code, cur_val)

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
        try:
            msg = '현금주문 완료, 코드: ' + code + ', 매수가: ' + str(price)
            self.comboBox_cond.addItems([msg])
            self.kiwoom.msg = msg
        except Exception as e:
            print(e)

    def send_order2(self, code, price, hoga='시장가', num=10):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()

        self.kiwoom.send_order("send_order_req", "0101",
                               account, order_type_lookup[order_type],
                               code, num, price, hoga_lookup[hoga], "")
        try:
            msg = '현금주문 완료, 코드: ' + code + ', 매수가: ' + str(price)
            self.comboBox_cond.addItems([msg])
            self.kiwoom.msg = msg
        except Exception as e:
            print(e)

    def timeout(self):
        current_time = QTime.currentTime()
        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결"
        else:
            state_msg = "서버 미 연결"

        self.statusbar.showMessage(state_msg + " | " + time_msg)
        if self.kiwoom.msg:
            try:
                # 텔레그램
                if self.check_box_receive_msg.isChecked():
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

    def search_cond(self):
        conditionIndex = self.comboBox_cond.currentText().split(';')[0]
        conditionName = self.comboBox_cond.currentText().split(';')[1]
        searched_codes = self.kiwoom.sendCondition("0", conditionName, int(conditionIndex), 1)
        # if self.pushButton_cond.text() == "적용":
        #     try:
        #         print('조건검색 조회')
        #         self.kiwoom.sendCondition("0", conditionName, int(conditionIndex), 1)
        #         self.pushButton_cond.setText("해제")
        #         self.comboBox_cond.setEnabled(False)
        #         # self.check_box_receive_msg.setEnabled(False)
        #         print("{} activated".format(conditionName))
        #
        #     except Exception as e:
        #         print('here?', e)  # 'Kiwoom' object has no attribute 'comboBox_cond'
        #
        # else:
        #     self.kiwoom.sendConditionStop("0", conditionName, conditionIndex)
        #     self.pushButton_cond.setText("적용")
        #     self.comboBox_cond.setEnabled(True)
        #     # self.check_box_receive_msg.setEnabled(True)
        return searched_codes


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
    data_queue = Queue()
    order_queue = Queue()
    myWindow = MyWindow(data_queue, order_queue)
    myWindow.show()
    app.exec_()
