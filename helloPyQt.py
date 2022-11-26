import sys
import pandas as pd
import pandas_datareader.data as web
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from pywinauto import application
from pywinauto import timings


# https: // wikidocs.net / 4236, PyQt 시작
def example01():
    app = QApplication(sys.argv)
    # print(sys.argv)  # 파이썬 스크립트 실행시 명령행 인자, [0]에는 스크립트 경로, [1] 부터 인자값
    label = QLabel("Hello PyQt")

    """
    UI를 구성하기 위한 코드가 배치
    """
    label1 = QPushButton("Quit")
    label2 = QPushButton(sys.argv[0])
    label.show()
    label1.show()
    label2.show()

    app.exec_()  # app을 통해 exec_ 메서드를 호출하면 프로그램은 이벤트 루프(event loop)에 진입
    # 이벤트 루프: 무한 반복하면서 이벤트를 처리하는 상태로, 일반적인 위에서 밑으로 순차 실행 후 종료되지 않고 윈도우가 계속 화면에 출력

    # https://devpouch.tistory.com/99


# https://wikidocs.net/4237, 윈도우를 화면에 표시
class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stock Trader')
        self.setGeometry(300, 300, 300, 600)

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        """
        참고로 대신증권과 이베스트투자증권의 클래스들에도 고유의 ProgID 값과 CLSID 값이 존재,
        이 값들은 윈도우 운영체제의 레지스트리에 등록됨. 
        CLSID는 16진수로 복잡하기 때문에 클래스 인스턴스를 생성할 때 보통 문자열로 된 ProgID를 사용.
        """
    #     btn1 = QPushButton("Log in", self)
    #     btn1.move(20, 20)
    #     btn1.clicked.connect(self.btn1_clicked)
    #
    #     btn2 = QPushButton('Check State', self)
    #     btn2.move(20, 70)
    #     btn2.clicked.connect(self.btn2_clicked)
    #
    # def btn1_clicked(self):
    #     # ret = self.kiwoom.dynamicCall('CommConnect()')
    #     self.kiwoom.dynamicCall('CommConnect()')  # 로그인 윈도우 실행, 0 반환 성공, 음수값 실패
    #
    # def btn2_clicked(self):
    #     if self.kiwoom.dynamicCall('GetConnectState()') == 0:
    #         self.statusBar().showMessage('Not Connected')
    #     else:
    #         self.statusBar().showMessage('Connected')

        self.kiwoom.dynamicCall('CommConnect()')

        self.event_logs = QTextEdit(self)
        self.event_logs.setGeometry(10, 60, 280, 80)
        self.event_logs.setEnabled(False)  # Log 표시창이므로 사용자의 편집 금지

        # OpenAPI의 Event 처리
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        label1 = QLabel("종목 코드", self)
        label1.move(20, 20)
        label1.setEnabled(False)

        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 20)
        self.code_edit.setEnabled(True)

        self.listwidget = QListWidget(self)
        self.listwidget.setGeometry(10, 150, 170, 300)

        btn1 = QPushButton('조회', self)
        btn1.move(190, 20)
        btn1.clicked.connect(self.btn1_clicked)

    def btn1_clicked(self):
        try:
            code = self.code_edit.text()
            self.event_logs.append('종목코드: ' + code)
            self.kiwoom.dynamicCall('SetInputValue(QString, QString)', '종목코드', code)
            self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', 'opt10001_req', 'opt10001', 0, '0101')
        except Exception as e:
            print(e)
        try:
            self.load_all_codes()
        except Exception as e:
            print(e)
        finally:
            pass

    def event_connect(self, err_code):
        if err_code == 0:
            self.event_logs.append('Success to Login')
            account_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"]).rstrip(';')
            self.event_logs.append("계좌번호: " + '*'*(len(account_num)-3) + account_num[-3:])
        else:
            self.event_logs.append('Fail to Login')

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == 'opt10001_req':
            name = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', trcode, '', rqname, 0, '종목명')
            volume = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', trcode, '', rqname, 0, '거래량')
            self.event_logs.append('종목명: ' + name.strip())
            self.event_logs.append('거래량: ' + volume.strip())

    def load_all_codes(self):
        # 0: 장내, 3: ELW, 4: 뮤추얼펀드, 5: 신주인수권, 6: 리츠, 8: ETF, 9: 하이일드펀드, 10: 코스닥, 30: 제3시장
        try:
            totallist_pd = pd.read_csv('data/code_list.csv', header=None)
            totallist = totallist_pd[[0, 1]].apply(lambda x: ': '.join(x.values.astype(str)), axis=1).tolist()
            self.listwidget.addItems(totallist)
        except Exception as e:
            self.event_logs.append(e + '저장된 목록이 없음, 새로 다운로드')
            kospi_code_list = self.kiwoom.dynamicCall('GetCodeListByMarket(QString)', ["0"])
            kospi_code_list = kospi_code_list.split(';')
            kosdaq_code_list = self.kiwoom.dynamicCall('GetCodeListByMarket(QString)', ['10'])
            kosdaq_code_list = kosdaq_code_list.split(';')
            # code_list = kospi_code_list.extend(kosdaq_code_list)
            kospi_codenm_list = [self.kiwoom.dynamicCall('GetMasterCodeName(QString)', [x])
                                 for x in kospi_code_list]
            kosdaq_codenm_list = [self.kiwoom.dynamicCall('GetMasterCodeName(QString)', [x])
                                  for x in kosdaq_code_list]
            kospi_pd = pd.DataFrame([kospi_code_list, kospi_codenm_list]).transpose()
            kosdaq_pd = pd.DataFrame([kosdaq_code_list, kosdaq_codenm_list]).transpose()
            totallist_pd = pd.concat([kospi_pd, kosdaq_pd], axis=0)
            totallist = totallist_pd[[0, 1]].apply(lambda x: ': '.join(x.values.astype(str)), axis=1).tolist()
            totallist_pd.to_csv('data/code_list.csv', index=False, header=None)
            self.listwidget.addItems(totallist)


def auto_update():
    update_app = application.Application()
    update_app.start("C:/OpenAPI/opversionup.exe")

    title = "업그레이드 확인"
    dlg = timings.WaitUntilPasses(10, 0.5, lambda: update_app.window_(title=title))

    btn_ctrl = dlg.Button0
    btn_ctrl.Click()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auto_update()  # 로그인 창을 실행하기 전에 업데이트 파일을 실행
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
