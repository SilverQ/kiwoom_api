from pywinauto import application
from pywinauto import timings
import time
import os

app = application.Application()
app.start("C:/OpenAPI/opversionup.exe")

title = "업그레이드 확인"
dlg = timings.WaitUntilPasses(10, 0.5, lambda: app.window_(title=title))

btn_ctrl = dlg.Button0
btn_ctrl.Click()

# # app = application.Application()
# app.start("C:/Kiwoom/KiwoomFlash2/khministarter.exe")
#
# title = "번개 Login"
# dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))
