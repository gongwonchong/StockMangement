from data import __data__
from data import checkvar
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# 데이터 수정창
class DataWindow:
    def __init__(self, top, value=None):
        master = QDialog(top, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.value = value
        # 처음 전체 잔량
        self.origin = 0
        self.setui(master)

    # label = [일자, 품목, 수량, 잔량, 0, 불출자, 비고]
    # vart = [QDateEdit(일자), QComboBox(품목), QRadioButton(입고), QRadioButton(출고), QSpinBox(수량),
    # , QLineEdit(불출자), QTextEdit(비고)]
    def setui(self, root):
        root.setFixedSize(500, 250)
        grid = QGridLayout(root)
        label = list()
        vart = list()

        label.append(QLabel("일자: "))
        grid.addWidget(label[0], 0, 0)

        vart.append(QDateEdit(datetime.datetime.today().date()))
        vart[0].setCalendarPopup(True)
        grid.addWidget(vart[0], 0, 1, 1, 3)

        label.append(QLabel("품목: "))
        grid.addWidget(label[1], 1, 0)

        vart.append(QComboBox())
        vart[1].addItem(" ")
        for t in __data__.select("select name from product"):
            vart[1].addItem(t[0])
        grid.addWidget(vart[1], 1, 1, 1, 3)

        vart.append(QRadioButton("입고"))
        vart.append(QRadioButton("출고"))

        label.append(QLabel("수량: "))
        grid.addWidget(label[2], 2, 0)

        vart.append(QSpinBox())
        vart[4].setRange(0, 2147483647)
        vart[4].setFixedSize(300, 22)
        grid.addWidget(vart[4], 2, 1)
        grid.addWidget(vart[2], 2, 2)
        grid.addWidget(vart[3], 2, 3)

        label.append(QLabel("잔량: "))
        grid.addWidget(label[3], 3, 0)

        label.append(QLabel(str(self.origin)))
        grid.addWidget(label[4], 3, 1, 1, 3)
        vart[4].valueChanged.connect(lambda: self.getcharge(vart[2], vart[3], label[4], vart[4].value()))
        vart[2].toggled.connect(lambda: self.getcharge(vart[2], vart[3], label[4], vart[4].value()))
        vart[3].toggled.connect(lambda: self.getcharge(vart[2], vart[3], label[4], vart[4].value()))
        vart[1].currentTextChanged.connect(lambda: self.setcharge(vart[2], vart[3], vart[1].currentText(), label[4],
                                                                  vart[4].value(), vart[0].date().toPyDate()))
        vart[0].dateChanged.connect(lambda: self.setcharge(vart[2], vart[3], vart[1].currentText(), label[4],
                                                           vart[4].value(), vart[0].date().toPyDate()))

        label.append(QLabel("불출자: "))
        grid.addWidget(label[5], 4, 0)

        vart.append(QLineEdit())
        grid.addWidget(vart[5], 4, 1, 1, 3)

        label.append(QLabel("비고: "))
        grid.addWidget(label[6], 5, 0)

        vart.append(QTextEdit())
        grid.addWidget(vart[6], 5, 1, 1, 3)

        if self.value is None:
            root.setWindowTitle("데이터 추가")
        else:
            root.setWindowTitle("데이터 수정")
            vart[0].setDate(self.value[0])

            t = vart[1].findText(self.value[1])
            if t != -1:
                vart[1].setCurrentIndex(t)

            # 입고가 0 이면
            if self.value[2] == 0:
                vart[4].setValue(self.value[3])
                vart[3].setChecked(True)
            # 출고가 0 이면
            elif self.value[3] == 0:
                vart[4].setValue(self.value[2])
                vart[2].setChecked(True)

            vart[5].setText(self.value[4])
            vart[6].setPlainText(self.value[5])

        confirm = QPushButton("확인")
        confirm.clicked.connect(lambda: self.confirmaction(vart, label[4], root, self.value is None))
        grid.addWidget(confirm, 6, 0, 1, 4)

        root.setLayout(grid)
        root.show()

    def confirmaction(self, input, charge, root, mode):
        result = list()
        result.append(input[0].date().toPyDate()) #0
        result.append(str(input[1].currentText())) #1
        result.append(input[2].isChecked()) #2 입고
        result.append(input[3].isChecked()) #3 츨고
        result.append(input[4].value()) #4
        result.append(str(input[5].text())) #5
        result.append(str(input[6].toPlainText())) #6
        msg = QMessageBox
        if result[1] == " ":
            msg.warning(root, "품명", "품명을 선택하지 않았습니다", QMessageBox.Ok)
            input[1].setFocus()
            return
        elif int(result[4]) == 0:
            msg.warning(root, "수량", "수량을 입력하지 않았습니다", QMessageBox.Ok)
            input[4].setFocus()
            return
        elif result[2] is False and result[3] is False:
            msg.warning(root, "입고 여부", "입고 여부를 선택하지 않았습니다", QMessageBox.Ok)
            input[2].setFocus()
            return
        elif int(str(charge.text())) < 0 and result[3]:
            msg.warning(root, "수량", "출고량이 잔량보다 많습니다", QMessageBox.Ok)
            input[4].setFocus()
            return
        elif result[5] == "":
            msg.warning(root, "불출자", "불출자를 입력하지 않았습니다", QMessageBox.Ok)
            input[5].setFocus()
            return
        product_date = result[0].strftime('%Y-%m-%d')
        # 추가모드
        if mode:
            # 입고
            if result[2]:
                sql = "insert into product_table(product_date, name, person, incnt, outcnt, note) values ('{}', " \
                      "'{}', '{}', '{}', 0, '{}')".format(product_date, result[1], result[5], result[4], result[6])
                __data__.other(sql)
                msg.information(root, "완료", "데이터를 입력했습니다.", QMessageBox.Ok)
                root.close()
            # 출고
            elif result[3]:
                sql = "insert into product_table(product_date, name, person, outcnt, incnt, note) values ('{}', " \
                      "'{}', '{}', '{}', 0, '{}')".format(product_date, result[1], result[5], result[4], result[6])
                __data__.other(sql)
                msg.information(root, "완료", "데이터를 입력했습니다.", QMessageBox.Ok)
                root.close()
        # 수정모드
        else:
            # 입고, 만약 출고에서 입고로 바뀌면 출고가 0이 됨
            if result[2]:
                sql = "update product_table set product_date = '{}', name = '{}', person = '{}', incnt = '{}'," \
                      " outcnt = '0', note = '{}' where id = '{}'" \
                    .format(product_date, result[1], result[5], result[4], result[6], self.value[-1])
                __data__.other(sql)
                msg.information(root, "완료", "데이터를 수정했습니다.", QMessageBox.Ok)
                root.close()
            # 출고, 만약 입고에서 출고로 바뀌면 입고가 0이 됨
            elif result[3]:
                sql = "update product_table set product_date = '{}', name = '{}', person = '{}', outcnt = '{}'," \
                      " incnt = '0', note = '{}' where id = '{}'"\
                    .format(product_date, result[1], result[5], result[4], result[6], self.value[-1])
                __data__.other(sql)
                __data__.other(sql)
                msg.information(root, "완료", "데이터를 수정했습니다.", QMessageBox.Ok)
                root.close()

    def getcharge(self, incnt, outcnt, charge, number):
        # 입고면 원값 + 입력 출고면 원값 - 입력
        if incnt.isChecked():
            charge.setText(str(int(self.origin) + number))
        elif outcnt.isChecked():
            charge.setText(str(int(self.origin) - number))

    def setcharge(self, incnt, outcnt, text, charge, number, datevalue):
        # 첫 잔량 설정
        if self.value is None:
            self.origin = checkvar(__data__.select("select sum(incnt) - sum(outcnt) from product_table where "
                                                   "product_date <= cast('{}' as date) and name = '{}'"
                                                   .format(datevalue, text))[0][0])
        else:
            self.origin = checkvar(__data__.select("select sum(incnt) - sum(outcnt) from product_table where "
                                                   "product_date <= cast('{}' as date) and name = '{}' and id < '{}'"
                                                   .format(datevalue, text, self.value[-1]))[0][0])
        self.getcharge(incnt, outcnt, charge, number)

