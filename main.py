import os
import re
import sys
import base64
import binascii
import contextlib
from src import GUI
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog


class Main(QMainWindow, GUI.Ui_MainWindow):
    base32_character = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567='
    base64_character = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon("./images/Logo.ico")) # 设置软件图标
        self.setFixedSize(self.width(), self.height()) # 禁止窗口最大化

        # 信号
        self.pushButton.clicked.connect(self.Decode)
        self.pushButton_2.clicked.connect(self.Clear)
        self.pushButton_3.clicked.connect(self.open_txt)

    def open_txt(self):
        filename = QFileDialog.getOpenFileNames(self, '选择文本', os.getcwd(), "Image Files(*.txt);;All Files(*)")
        if filename[0] != []:
            GUI.MyQPlanTextEdit.read_txt(self.plainTextEdit, filename[0][0])

    def get_text(self):
        if (text := self.plainTextEdit.toPlainText()) != "":
            return text
        QMessageBox.information(self, "温馨提示", "您输入的内容为空!", QMessageBox.Yes)

    def Basestr_to_List(self, base_str):
        return base_str.splitlines()

    def is_conform(self, base_str):
        ''' base_str是否符合要求 '''
        data = self.Basestr_to_List(base_str)
        data = "".join(data)
        
        if all(i in self.base32_character or i in self.base64_character for i in data):
            return True
        QMessageBox.information(self, "温馨提示", "您输入的内容不符合Base32或Base64编码!", QMessageBox.Yes)

    def ShowInfo(self, base_Comple, bin_str, ascii_str):
        self.pushButton.setEnabled(True)
        self.plainTextEdit_2.setPlainText(base_Comple)
        self.plainTextEdit_3.setPlainText(bin_str)
        self.plainTextEdit_4.setPlainText(ascii_str)

    def Decode(self):
        # 判断是否输入框是否为空
        if (base_str := self.get_text()) is not None:
            # 判断输入框类容是否符合要求
            if self.is_conform(base_str) is not None:
                self.pushButton.setEnabled(False)

                self.workThread = WorkThread(base_str)
                self.workThread.end.connect(self.ShowInfo)
                self.workThread.start()

    def Clear(self):
        self.plainTextEdit.clear()
        self.plainTextEdit_2.clear()
        self.plainTextEdit_3.clear()
        self.plainTextEdit_4.clear()

class WorkThread(QtCore.QThread):
    end = QtCore.pyqtSignal(str, str, str)

    def __init__(self, base_str) -> None:
        super().__init__()
        self.base_str = base_str

    def Completion(self, base_str, type=1):
        # 0表示base32补全=, 1表示base64补全=
        data = ui.Basestr_to_List(base_str)
        base_Comple = ""
        for line in data:
            if type == 1:
                if (missing_padding := len(line) % 4) != 0:
                    line += "=" * (4 - missing_padding)
            elif type == 0:
                if (missing_padding := len(line) % 8) != 0:
                    line += "=" * (8 - missing_padding)
            base_Comple += f"{line}\n"
        return base_Comple

    def get_base32_diff_value(self, line, normal_line):
        return next((abs(ui.base32_character.index(line[i]) - ui.base32_character.index(normal_line[i])) for i in range(len(normal_line)) if line[i] != normal_line[i]), 0)

    def Base32_Steganography(self, base32_str, padding=False):
        data = ui.Basestr_to_List(base32_str)

        bin_str = ''
        for line in data:
            with contextlib.suppress(binascii.Error):
                normal_line = base64.b32encode(base64.b32decode(line.encode())).decode()
                diff = self.get_base32_diff_value(line, normal_line)
                if '=' not in line:
                    continue

                pads_num = line.count("=")
                if diff:
                    bin_str += bin(diff)[2:].zfill(5 * (8 - pads_num) % 8) if padding else bin(diff)[2:]
                else:
                    bin_str += '0' * (5 *(8 - pads_num) % 8) if padding else '0'
        return bin_str

    def Base64_Steganography(self, base64_str):
        data = ui.Basestr_to_List(base64_str)

        bin_str = ""
        for line in data:
            if re.search("==$", line):
                bin_str += bin(ui.base64_character.index(line[-3]))[2:].zfill(8)[-4:]
            elif re.search("=$", line):
                bin_str += bin(ui.base64_character.index(line[-2]))[2:].zfill(8)[-2:]
        return bin_str

    def run(self):
        if ui.radioButton.isChecked():
            base_Comple = self.Completion(self.base_str, type=0)
            bin_str = self.Base32_Steganography(base_Comple, padding=False)
        elif ui.radioButton_2.isChecked():
            base_Comple = self.Completion(self.base_str, type=1)
            bin_str = self.Base64_Steganography(base_Comple)
        elif ui.radioButton_3.isChecked():
            base_Comple = self.Completion(self.base_str, type=0)
            bin_str = self.Base32_Steganography(base_Comple, padding=True)
        ascii_str = "".join(chr(int(bin_str[i:i+8], 2)) for i in range(0, len(bin_str), 8))
        self.end.emit(base_Comple, bin_str, ascii_str)

if __name__ == "__main__":
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling) # DPI自适应
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())