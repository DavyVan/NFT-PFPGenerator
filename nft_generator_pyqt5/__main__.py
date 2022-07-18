import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QStatusBar, QDialog, \
    QLabel, QWidget, QLineEdit, QProgressBar, QSizePolicy, QFileDialog, QSpinBox
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
# from PyQt5 import Qt
from threading import Thread


STANDARD_WIDGET_HEIGHT = 30


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # global state
        self.resource_path = None
        self.resource_path_lineedit = None
        self.output_path = None
        self.output_path_lineedit = None
        self.count = 0
        self.progress_bar = None

        self.setWindowTitle("NFT Generator")
        # self.setFixedSize(800, 300)
        self.setMinimumSize(800, 200)


        # the root vbox
        root_vbox = QVBoxLayout()

        # 1st row: label, lineedit(disabled), button for filedialog
        row1_hbox = QHBoxLayout()

        row1_label = QLabel("素材文件夹：")
        row1_hbox.addWidget(row1_label)

        row1_lineedit = QLineEdit("请点击右侧按钮选择文件夹→")
        row1_lineedit.setEnabled(False)
        row1_hbox.addWidget(row1_lineedit)
        self.resource_path_lineedit = row1_lineedit

        row1_filedialog_button = QPushButton("浏览…")
        row1_filedialog_button.clicked.connect(self.row1_filedialog_button_clicked)
        row1_hbox.addWidget(row1_filedialog_button)

        root_vbox.addLayout(row1_hbox)
        
        # 2nd row: same widgets as the 1st row, but for output
        row2_hbox = QHBoxLayout()

        row2_label = QLabel("输出文件夹：")
        row2_hbox.addWidget(row2_label)

        row2_lineedit = QLineEdit("请点击右侧按钮选择文件夹→")
        row2_lineedit.setEnabled(False)
        row2_hbox.addWidget(row2_lineedit)
        self.output_path_lineedit = row2_lineedit

        row2_filedialog_button = QPushButton("浏览…")
        row2_filedialog_button.clicked.connect(self.row2_filedialog_button_clicked)
        row2_hbox.addWidget(row2_filedialog_button)

        root_vbox.addLayout(row2_hbox)

        # 3rd row: label, input for count
        row3_hbox = QHBoxLayout()

        row3_label = QLabel("生成数量：")
        row3_hbox.addWidget(row3_label)

        row3_count_spinbox = QSpinBox()
        row3_count_spinbox.setMinimum(0)
        row3_count_spinbox.setMaximum(2147483647)
        row3_count_spinbox.setValue(0)
        row3_count_spinbox.setSingleStep(100)
        row3_count_spinbox.valueChanged.connect(self.row3_count_spinbox_value_changed)
        row3_hbox.addWidget(row3_count_spinbox)

        root_vbox.addLayout(row3_hbox)

        # 4th row: button for start
        row4_start_button = QPushButton("开始")
        row4_start_button.clicked.connect(self.row4_start_button_clicked)
        row4_start_button.setFixedWidth(400)
        root_vbox.addWidget(row4_start_button)
        root_vbox.setAlignment(row4_start_button, Qt.AlignHCenter)

        # progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setFixedWidth(400)
        root_vbox.addWidget(progress_bar)
        root_vbox.setAlignment(progress_bar, Qt.AlignHCenter)
        self.progress_bar = progress_bar

        # bind the root vbox to the main window
        root_widget = QWidget()
        root_widget.setLayout(root_vbox)
        self.setCentralWidget(root_widget)

        # # status bar
        # status_bar = QStatusBar(self)
        # self.setStatusBar(status_bar)

    def row1_filedialog_button_clicked(self):
        print("clicked!")
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.exec()
        selected_dir = file_dialog.selectedFiles()
        if len(selected_dir) > 0:
            print(selected_dir[0])
            self.resource_path = selected_dir[0]
            self.resource_path_lineedit.setText(self.resource_path)

    def row2_filedialog_button_clicked(self):
        print("clicked!")
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.exec()
        selected_dir = file_dialog.selectedFiles()
        if len(selected_dir) > 0:
            print(selected_dir[0])
            self.output_path = selected_dir[0]
            self.output_path_lineedit.setText(self.output_path)

    def row3_count_spinbox_value_changed(self, value):
        print(value)
        self.count = value

    def row4_start_button_clicked(self):
        print("started!")
        self.progress_bar.setMaximum(self.count)
        Thread(target=self.worker_thread).start()
        # TODO: cannot allow two workers
        # TODO: check all the inputs


    def worker_thread(self):
        for i in range(10):
            time.sleep(1)
            self.progress_bar.setValue(i+1)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
