from pymysql import *


class productdb:
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


__data__ = productdb()

def checkvar(var):
    if var is None:
        return "0"
    else:
        return var
