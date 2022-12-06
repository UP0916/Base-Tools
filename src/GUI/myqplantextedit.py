import os
import re
from PyQt5 import QtCore, QtGui, QtWidgets

class MyQPlanTextEdit(QtWidgets.QPlainTextEdit):
    character = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\r\n"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        super().dragEnterEvent(e)
        self.file_path = e.mimeData().text().replace('file:///', '')
        if self.file_path.endswith('.txt'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        super().dropEvent(e)
        
        # 如果文件存在读取文件
        if os.path.exists(self.file_path):
            # 首先清除输入框 file:///...
            self.clear()
            # 一行一行读取
            with open(self.file_path, 'rb') as f:
                for row, line in enumerate(f):
                    if all(char in self.character for char in line):
                        self.insertPlainText(line.decode("utf-8"))
                    else:
                        self.insertPlainText("".join(chr(char) for char in line if char in self.character))
                        QtWidgets.QMessageBox.warning(self, "温馨提示", f"当前文本的第{row + 1}行可能存在零宽字符, 可以使用Sublime Text检查文本, 目前已帮您强制读取!", QtWidgets.QMessageBox.Yes)
        else:
            QtWidgets.QMessageBox.critical(self, "温馨提示", "文件不存在!", QtWidgets.QMessageBox.Yes)
        
            
