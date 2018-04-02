from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
from pymysql import *


class productdb_source:
    def __init__(self):
        self.source = Connect(host='localhost', user='root', password='mariadb', database='productdb', charset='utf8')
        self.cursor = self.source.cursor()

    # 조회 SQL
    def select(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result is None:
                return list()
            else:
                return result
        except InternalError as e:
            code, message = e.args
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("데이터베이스 오류")
            if code == 1241:
                msg.setText("중복된 데이터가 있습니다.")
            else:
                msg.setText(message)
            msg.exec()

    # 기타 SQL
    def other(self, sql):
        try:
            self.cursor.execute(sql)
            self.source.commit()
        except InternalError as e:
            code, message = e.args
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("데이터베이스 오류")
            if code == 1241:
                msg.setText("중복된 데이터가 있습니다.")
            else:
                msg.setText(message)
            msg.exec()


    # 연결 종료
    def __del__(self):
        self.source.close()


__data__ = productdb_source()


class MainWindow:
    def __init__(self):
        master = QWidget()
        # 표의 모델
        self.model = QStandardItemModel()
        # 받을 데이터 목록
        self.origin = list()
        # 필터링할 일자
        ty = datetime.datetime.today().date().year
        tm = datetime.datetime.today().date().month
        self.startdate = datetime.date(ty, tm, 1)
        self.enddate = datetime.datetime.today().date()
        self.idx = -1
        self.setui(master)

    def setui(self, root):
        root.setWindowTitle("창고 관리")
        grid = QGridLayout(root)

        # 메뉴
        menu = QMenuBar()
        menu.addAction("추가", lambda: self.insertdata(root))
        menu.addAction("수정", lambda: self.moddata(root, self.idx))
        menu.addAction("삭제", lambda: self.deldata(root))
        menu.addAction("품목 관리", lambda: self.showproduct(root))
        menu.addAction("전체 조회", lambda: self.refresh(self.getalldata()))
        grid.addWidget(menu, 0, 0, 1, 3)

        # 시작일
        sdate = QDateEdit(self.startdate)
        sdate.setCalendarPopup(True)
        grid.addWidget(sdate, 1, 0)

        # 마지막 일
        edate = QDateEdit(self.enddate)
        edate.setCalendarPopup(True)
        grid.addWidget(edate, 1, 1)

        # 조회
        viewb = QPushButton("조회")
        viewb.setFixedSize(100, 22)
        viewb.clicked.connect(lambda: self.viewdata(sdate.date(), edate.date()))
        grid.addWidget(viewb, 1, 2)

        # 표 헤더
        i = 0
        for t in ['일시', '품목', '입고', '출고', '불출자', '비고']:
            c = QStandardItem(t)
            c.setTextAlignment(Qt.AlignCenter)
            self.model.setHorizontalHeaderItem(i, c)
            i = i + 1
        table = QTreeView()
        table.setModel(self.model)
        for i in range(0, 6):
            table.header().resizeSection(i, root.size().width() // 6 + 200)
        # 선택 이벤트
        table.selectionModel().selectionChanged.connect(lambda: self.onselected(table.selectionModel()))
        grid.addWidget(table, 2, 0, 1, 3)
        root.setLayout(grid)
        root.showMaximized()

    # 데이터 받아서 모델에 삽입
    def refresh(self, table):
        self.model.removeRows(0, self.model.rowCount())
        # 데이터를 원소스에 저장
        # 모델은 원소스 순서대로 저장됨
        self.origin = table
        # 데이터가 있으면 모델에 삽입 (모델은 표의 실제 데이터)
        if len(self.origin) != 0:
            for row in self.origin:
                t = list()
                for column in row:
                    if str(column) == "None":
                        column = "0"
                    c = QStandardItem(str(column))
                    c.setTextAlignment(Qt.AlignCenter)
                    t.append(c)
                self.model.appendRow(t)
            self.model.setColumnCount(len(self.origin[0]) - 1)

    # 선택 이벤트 핸들링 만약 선택되면 선택값의 인덱스를 저장
    def onselected(self, model):
        if model.hasSelection():
            self.idx = model.selectedIndexes()[0].row()
        else:
            self.idx = -1

    def viewdata(self, sdate, edate):
        # 날짜 변경하고 조회
        self.chdate(sdate.toPyDate(), edate.toPyDate())
        self.refresh(self.getdatabydate())

    def chdate(self, sdate, edate):
        self.startdate = sdate
        self.enddate = edate

    def getdatabydate(self):
        # 데이터 얻기
        sql = "select product_date, name, incnt, outcnt, person, note, id from product_table where product_date " \
              "between cast('{}' as date) and cast('{}' as date) order by product_date asc, id asc"\
            .format(self.startdate.strftime('%Y-%m-%d'), self.enddate.strftime('%Y-%m-%d'))
        return __data__.select(sql)

    def getalldata(self):
        sql = "select product_date, name, incnt, outcnt, person, note, id from product_table order by product_date asc, " \
              "id asc"
        return __data__.select(sql)

    # 데이터 삭제
    def deldata(self, root):
        if self.idx == -1:
            QMessageBox().warning(root, "데이터 오류", "삭제할 데이터를 선택하지 않았습니다.", QMessageBox.Ok)
            return
        # 삭제할 데이터 내용
        detailed = "일시: " + str(self.origin[self.idx][0]) + "\n" + "품목: " + self.origin[self.idx][1] + "\n" + \
                   "입고: " + str(self.origin[self.idx][2]) + "\n" + "출고: " + str(self.origin[self.idx][3]) + \
                   "\n" + "불출자: " + str(self.origin[self.idx][4]) + "\n비고: " + str(self.origin[self.idx][5])
        # 삭제 여부 확인 후 삭제
        msg = QMessageBox()
        msg.setDetailedText(detailed)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setWindowTitle("삭제")
        msg.setText("정말로 데이터를 삭제하시겠습니까?")
        t = msg.exec_()
        if t == QMessageBox.Yes:
            sql = "delete from product_table where id = '{}'".format(self.origin[self.idx][-1])
            __data__.other(sql)
            msg.information(root, "완료", "데이터를 삭제했습니다.", QMessageBox.Ok)

    # 데이터 수정창 띄우기
    #
    def moddata(self, master, idx):
        if self.idx == -1:
            QMessageBox().warning(master, "데이터 오류", "수정할 데이터를 선택하지 않았습니다.", QMessageBox.Ok)
            return
        DataWindow(master, self.origin[idx])

    @staticmethod
    # 데이터 삽입 창 띄우기
    def insertdata(master):
        DataWindow(master)

    @staticmethod
    # 품목 관리 창 띄우기
    def showproduct(master):
        ProductWindow(master)


# 데이터 삽입/수정 창
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

class ProductWindow:
    def __init__(self, top):
        master = QDialog(top, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.origin = list()
        self.model = QStandardItemModel()
        self.idx = -1
        self.setui(master)

    def setui(self, root):
        root.setFixedSize(700, 700)
        root.setModal(True)
        root.setWindowTitle("품목 관리")
        grid = QGridLayout(root)

        c = QStandardItem('품목')
        c.setTextAlignment(Qt.AlignCenter)
        self.model.setHorizontalHeaderItem(0, c)

        c = QStandardItem('내용')
        c.setTextAlignment(Qt.AlignCenter)
        self.model.setHorizontalHeaderItem(1, c)

        self.refresh()

        update = QPushButton("수정")
        update.setEnabled(False)
        update.clicked.connect(lambda: self.moddata(root))
        rm = QPushButton("삭제")
        rm.setEnabled(False)
        rm.clicked.connect(lambda: self.deldata(root))

        table = QTreeView()
        table.setModel(self.model)
        table.header().resizeSection(0, root.size().width() // 2)
        table.header().resizeSection(1, root.size().width() // 2)
        table.selectionModel().selectionChanged.connect(lambda: self.onselected(table.selectionModel(), rm, update))
        grid.addWidget(table, 0, 0, 1, 3)

        add = QPushButton("추가")
        add.clicked.connect(lambda: self.adddata(root))
        grid.addWidget(add, 1, 0)
        grid.addWidget(update, 1, 1)
        grid.addWidget(rm, 1, 2)

        root.setLayout(grid)
        root.show()

    def onselected(self, model, rm, update):
        if model.hasSelection():
            self.idx = model.selectedIndexes()[0].row()
            rm.setEnabled(True)
            update.setEnabled(True)
        else:
            self.idx = -1
            rm.setEnabled(False)
            update.setEnabled(False)

    def refresh(self):
        self.model.removeRows(0, self.model.rowCount())
        self.origin = self.getdata()
        if len(self.origin) != 0:
            for row in self.origin:
                t = list()
                for column in row:
                    if str(column) == "None":
                        column = "0"
                    c = QStandardItem(str(column))
                    c.setTextAlignment(Qt.AlignCenter)
                    t.append(c)
                self.model.appendRow(t)

    def getdata(self):
        sql = "SELECT name, detail FROM product"
        return __data__.select(sql)

    def adddata(self, root):
        ProductDataWindow(root, self.refresh)

    def moddata(self, root):
        ProductDataWindow(root, self.refresh, self.origin[self.idx])

    def deldata(self, root):
        effectedcontent = "\n삭제될 수 있는 데이터: \n"
        sql = "select product_date, name, incnt, outcnt, person, note from product_table where name = '{}'".\
            format(self.origin[self.idx][0])
        sqlresult = __data__.select(sql)
        if sqlresult is not None:
            for t in sqlresult:
                effectedcontent += "\n일시 : {}\n품목 : {}\n입고 : {}\n출고 : {}\n불출자 : {}".\
                    format(t[0], t[1], t[2], t[3], t[4], t[5])
        else:
            effectedcontent += "없음"
        detailed = "품목: " + self.origin[self.idx][0] + "\n" + "설명: " + self.origin[self.idx][1] + effectedcontent
        msg = QMessageBox()
        msg.setDetailedText(detailed)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setWindowTitle("삭제")
        msg.setText("정말로 데이터를 삭제하시겠습니까?")
        t = msg.exec_()
        if t == QMessageBox.Yes:
            sql = "delete from product where name = '{}'".format(self.origin[self.idx][0])
            __data__.other(sql)
            sql = "delete from product_table where name = '{}'".format(self.origin[self.idx][0])
            __data__.other(sql)
            msg.information(root, "완료", "데이터를 삭제했습니다.", QMessageBox.Ok)
            self.refresh()


class ProductDataWindow:
    def __init__(self, top, refresh, value=None):
        master = QDialog(top, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.origin = list()
        self.refresh = refresh
        self.model = QStandardItemModel()
        self.value = value
        self.setui(master)

    def setui(self, root):
        root.setFixedSize(300, 200)
        grid = QGridLayout(root)
        label = list()
        vart = list()
        label.append(QLabel("품명: "))
        grid.addWidget(label[0], 0, 0)
        vart.append(QLineEdit())
        grid.addWidget(vart[0], 0, 1)

        label.append(QLabel("내용: "))
        grid.addWidget(label[1], 1, 0)
        vart.append(QTextEdit())
        grid.addWidget(vart[1], 1, 1)

        confirm = QPushButton("확인")
        confirm.clicked.connect(
            lambda: self.confirmAction(data=[vart[0].text(), vart[1].toPlainText()],name=vart[0],
                                       root=root))
        grid.addWidget(confirm, 2, 0, 1, 2)

        if self.value is None:
            root.setWindowTitle("데이터 추가")
        else:
            root.setWindowTitle("데이터 수정")
            vart[0].setText(self.value[0])
            vart[1].setPlainText(self.value[1])

        root.setLayout(grid)
        root.show()

    def confirmAction(self, data, name, root):
        msg = QMessageBox()
        if data[0] == "":
            msg.warning(root, "품명", "품명을 입력하지 않았습니다", QMessageBox.Ok)
            name.setFocus()
        else:
            # 품명 수정일경우
            if self.value is not None and data[0] != self.value[0]:
                effectedcontent = "\n변경될 수 있는 데이터: \n"
                sql = "select product_date, name, incnt, outcnt, person, note from product_table where name = '{}'". \
                    format(self.value[0])
                sqlresult = __data__.select(sql)
                if sqlresult is not None:
                    for t in sqlresult:
                        effectedcontent += "\n일시 : {}\n품목 : {}\n입고 : {}\n출고 : {}\n불출자 : {}". \
                            format(t[0], t[1], t[2], t[3], t[4], t[5])
                else:
                    effectedcontent += "없음"
                detailed = "품목: " + self.value[0] + "\n" + "설명: " + self.value[1] + effectedcontent
                msg = QMessageBox()
                msg.setDetailedText(detailed)
                msg.setIcon(QMessageBox.Question)
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setWindowTitle("수정")
                msg.setText("정말로 데이터를 수정하시겠습니까?")
                t = msg.exec_()
                if t == QMessageBox.Yes:
                    sql = "update product_table set name = '{0}' where name = '{1}'".format(data[0], self.value[0])
                    __data__.other(sql)
                    sql = "delete from product where name = '{}'".format(self.value[0])
                    __data__.other(sql)
                elif t == QMessageBox.No:
                    return
            sql = "replace into product (name, detail) values ('{0}', '{1}')".format(data[0], data[1])
            __data__.other(sql)
            self.refresh()
            root.close()


def checkvar(var):
    if var is None:
        return "0"
    else:
        return var
