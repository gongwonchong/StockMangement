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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())