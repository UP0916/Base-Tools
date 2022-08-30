import sys
import base64
from src import GUI
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox


class Main(QMainWindow, GUI.Ui_MainWindow):
    character = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon("./images/Logo.ico")) # 设置软件图标
        self.setFixedSize(self.width(), self.height()) # 禁止窗口最大化

        # 信号
        self.pushButton.clicked.connect(self.Decode)

    def get_text(self):
        if (text := self.plainTextEdit.toPlainText()) != "":
            return text
        QMessageBox.information(self, "温馨提示", "您输入的内容为空!", QMessageBox.Yes)

    def is_conform(self, base64_str):
        ''' base64_str是否符合要求 '''
        data = self.Base64str_to_List(base64_str)
        data = "".join(data)
        
        if all(i in self.character for i in data):
            return True
        QMessageBox.information(self, "温馨提示", "您输入的内容只能是0或者1!", QMessageBox.Yes)

    def Base64str_to_List(self, base64_str):
        return base64_str.splitlines()

    def Completion(self, base64_str):
        data = self.Base64str_to_List(base64_str)

        base64_Comple = ""
        for line in data:
            missing_padding = len(line) % 4
            if missing_padding != 0:
                line += "=" * (4 - missing_padding)
            base64_Comple += f"{line}\n"
        return base64_Comple
    
    def Base64_Steganography(self, base64_str):
        data = self.Base64str_to_List(base64_str)

        bin_str = ""
        for cipher in data:
            flag = 0
            if cipher[-1:] == "=":
                flag = 1
                if cipher[-2:] == "==":
                    flag = 2
            
            if flag == 1:
                bin_str += bin(self.character.index(cipher[-2]))[2:].zfill(8)[-2:]
            elif flag == 2:
                bin_str += bin(self.character.index(cipher[-3]))[2:].zfill(8)[-4:]
        return bin_str

    def ShowInfo(self, base64_Comple, bin_str, ascii_str):
        self.plainTextEdit_2.setPlainText(base64_Comple)
        self.plainTextEdit_3.setPlainText(bin_str)
        self.plainTextEdit_4.setPlainText(ascii_str)

    def Decode(self):
        # 判断是否输入框是否为空
        if (base64_str := self.get_text()) is not None:
            # 判断输入框类容是否符合要求
            if self.is_conform(base64_str) is not None:
                base64_Comple = self.Completion(base64_str)
                bin_str = self.Base64_Steganography(base64_Comple)
                ascii_str = "".join(chr(int(bin_str[i:i+8], 2)) for i in range(0, len(bin_str), 8))
                self.ShowInfo(base64_Comple, bin_str, ascii_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())