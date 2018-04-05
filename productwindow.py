from data import __data__
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

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