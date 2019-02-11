# -*- coding: utf-8 -*-
import os
import sys
import xml.etree.ElementTree as ET

from Paginator import Paginator
from mainwindow import Ui_MainWindow
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView, QMessageBox


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('xml-icon.png'))
        self.tableWidget.setHorizontalHeaderLabels(("#", "Дата/Время", "IP", "Логин", "Клиент", "Политика"))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setVisible(False)
        self.openButton.clicked.connect(self.openFile)
        self.prevButton.clicked.connect(self.prevPage)
        self.nextButton.clicked.connect(self.nextPage)

        self.paginator = None
        self.pagesize = 50
        self.currentpage = 1
        self.filename = ""

    def openFile(self):
        self.filename = QFileDialog.getOpenFileName(self, "", "",
                                                    "Log Files (*.log);;"
                                                    "XML Files (*.xml);;"
                                                    "All Files (*)")[0]
        if self.filename:
            self.lineEdit.setText(self.filename)
            self.paginator = Paginator(self.filename, self.pagesize)
            self.preparePage()

    def preparePage(self):
        lines = self.paginator.getPage(self.currentpage)
        if len(lines) == 0:
            self.showError(type =1)

        self.tableWidget.setRowCount(0)
        for line in lines:
            try:
                self.putLine(LogLine(line))
            except ET.ParseError:
                print('Parse error')

        self.prevButton.setDisabled(self.currentpage <= 1)
        self.nextButton.setDisabled(len(lines) < self.pagesize)

    def prevPage(self):
        self.currentpage -= 1
        self.preparePage()

    def nextPage(self):
        self.currentpage += 1
        self.preparePage()

    def putLine(self, line):
        position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(position)
        if line.vars["Reason-Code"] == '16':
            color = QBrush(QColor(255, 192, 203))
        else:
            color = QBrush(QColor(255, 255, 255))

        for var in line.vars:
            if var == 'Reason-Code':
                continue
            item = QTableWidgetItem(line.vars[var])
            item.setBackground(color)
            self.tableWidget.setItem(position, list(line.vars.keys()).index(var), item)

        item = QTableWidgetItem(str(position +1 + (self.currentpage - 1) * self.pagesize))
        item.setBackground(color)
        self.tableWidget.setItem(position, 0, item)

    def showError(self, type = 0):
        msg = QMessageBox(self)
        if type:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Нет данных")
            msg.setWindowTitle("Внимание")
        else:
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка чтения файла")
            msg.setWindowTitle("Ошибка")
        msg.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.filename = path
                self.currentpage = 1
                self.lineEdit.setText(self.filename)
                self.paginator = Paginator(self.filename, self.pagesize)
                self.preparePage()


class LogLine:
    def __init__(self, line):
        self.vars = {}
        vars_list = ["Reason-Code", "Timestamp", "NAS-IP-Address",
                     "User-Name", "Client-Friendly-Name", "NP-Policy-Name"]
        root = ET.fromstring(line)
        for var in vars_list:
            result = root.find(var)
            if result is not None:
                self.vars[var] = result.text.encode("ansi").decode("utf-8")
            else:
                self.vars[var] = ""


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
