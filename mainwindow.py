import sys
import datetime
from productwindow import *
from data import __data__
from datawindow import *
from PyQt5.QtWidgets import *

class MainWindow:
    def __init__(self):
        master = QWidget()
        # 표의 모델
        self.model = QStandardItemModel()
        # 필터링할 일자
        ty = datetime.datetime.today().date().year
        tm = datetime.datetime.today().date().month
        self.startdate = datetime.date(ty, tm, 1)
        self.enddate = datetime.datetime.today().date()
        self.idx = -1
        self.idxes = list()
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
        for t in ['일시', '품목', '입고', '출고', "잔량", '불출자', '비고']:
            c = QStandardItem(t)
            c.setTextAlignment(Qt.AlignCenter)
            self.model.setHorizontalHeaderItem(i, c)
            i = i + 1
        table = QTreeView()
        table.setModel(self.model)
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # 선택 이벤트
        table.selectionModel().selectionChanged.connect(lambda: self.onselected(table.selectionModel()))
        grid.addWidget(table, 2, 0, 1, 3)
        root.setLayout(grid)
        root.showMaximized()

    # 데이터 받아서 모델에 삽입
    def refresh(self, table):
        self.idxes.clear()
        self.model.removeRows(0, self.model.rowCount())
        # 모델은 원소스 순서대로 저장됨
        # 데이터가 있으면 모델에 삽입 (모델은 표의 실제 데이터)
        if len(table) != 0:
            for row in table:
                t = list()
                for column in row:
                    if str(column) == "None":
                        column = "0"
                    c = QStandardItem(str(column))
                    c.setTextAlignment(Qt.AlignCenter)
                    t.append(c)
                self.model.appendRow(t)
                self.idxes.append(row[-1])
            self.model.setColumnCount(len(table[0]) - 1)

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
        # 기간별 데이터 얻기
        sql = "select product_date, name, incnt, outcnt, (select sum(t.incnt) - sum(t.outcnt) from product_table as t " \
              "where t.id <= p.id and t.product_date <= p.product_date and t.name = p.name), person, note, id from " \
              "product_table as p where product_date between cast('{}' as date) and cast('{}' as date) order by " \
              "product_date asc, id asc"\
            .format(self.startdate.strftime('%Y-%m-%d'), self.enddate.strftime('%Y-%m-%d'))
        return __data__.select(sql)

    def getalldata(self):
        # 전체 데이터 얻기
        sql = "select product_date, name, incnt, outcnt, (select sum(t.incnt) - sum(t.outcnt) from product_table as t " \
              "where t.id <= p.id and t.product_date <= p.product_date and t.name = p.name), person, note, id from " \
              "product_table as p order by product_date asc, id asc"
        return __data__.select(sql)

    # 데이터 삭제
    def deldata(self, root):
        if self.idx == -1:
            QMessageBox().warning(root, "데이터 오류", "삭제할 데이터를 선택하지 않았습니다.", QMessageBox.Ok)
            return
        table = "select product_date, name, incnt, outcnt, person, note, id from product_table id =" + \
                str(self.idxes[self.idx])
        # 삭제할 데이터 내용
        detailed = "일시: " + str(table[0][0]) + "\n" + "품목: " + table[0][1] + "\n" + "입고: " + str(table[0][2]) + \
                   "\n" + "출고: " + str(table[0][3]) + "\n" + "불출자: " + str(table[0][4]) + "\n비고: " + \
                   str(table[0][5])
        # 삭제 여부 확인 후 삭제
        msg = QMessageBox()
        msg.setDetailedText(detailed)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setWindowTitle("삭제")
        msg.setText("정말로 데이터를 삭제하시겠습니까?")
        t = msg.exec_()
        if t == QMessageBox.Yes:
            sql = "delete from product_table where id = '{}'".format(str(self.idxes[self.idx]))
            __data__.other(sql)
            msg.information(root, "완료", "데이터를 삭제했습니다.", QMessageBox.Ok)

    # 데이터 수정창 띄우기
    #
    def moddata(self, master, idx):
        if self.idx == -1:
            QMessageBox().warning(master, "데이터 오류", "수정할 데이터를 선택하지 않았습니다.", QMessageBox.Ok)
            return
        sql = "select product_date, name, incnt, outcnt, person, note, id from product_table where id =" + \
              str(self.idxes[idx])
        DataWindow(master, __data__.select(sql)[0])

    @staticmethod
    # 데이터 삽입 창 띄우기
    def insertdata(master):
        DataWindow(master)

    @staticmethod
    # 품목 관리 창 띄우기
    def showproduct(master):
        ProductWindow(master)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
