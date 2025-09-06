# Form implementation generated from reading ui file 'main.ui'
# PyQt6 UI code generator 6.9.0
# WARNING: Manual changes will be preserved, but future pyuic6 runs may overwrite.

from PyQt6 import QtCore, QtGui, QtWidgets
import logging


class Ui_Form(object):
    def setupUi(self, Form, get_image_path_func=None):
        Form.setObjectName("Form")
        Form.resize(381, 360)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(381, 360))
        Form.setMaximumSize(QtCore.QSize(381, 360))

        # --- Labels ---
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(7, 0, 371, 32))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")

        # Load image1.png safely (via injected func)
        if get_image_path_func:
            img_path = get_image_path_func("image1.png")
            if img_path:
                self.label.setPixmap(QtGui.QPixmap(img_path))
            else:
                logging.error("image1.png could not be loaded in UI")

        self.label_3 = QtWidgets.QLabel(parent=Form)
        self.label_3.setGeometry(QtCore.QRect(320, 0, 51, 41))
        self.label_3.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(parent=Form)
        self.label_4.setGeometry(QtCore.QRect(10, 30, 51, 21))
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.label_5.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_5.setObjectName("label_5")

        self.label_6 = QtWidgets.QLabel(parent=Form)
        self.label_6.setGeometry(QtCore.QRect(110, 50, 91, 16))
        self.label_6.setObjectName("label_6")

        self.label_8 = QtWidgets.QLabel(parent=Form)
        self.label_8.setGeometry(QtCore.QRect(10, 120, 61, 16))
        self.label_8.setObjectName("label_8")

        self.label_9 = QtWidgets.QLabel(parent=Form)
        self.label_9.setGeometry(QtCore.QRect(10, 160, 61, 16))
        self.label_9.setObjectName("label_9")

        self.label_10 = QtWidgets.QLabel(parent=Form)
        self.label_10.setGeometry(QtCore.QRect(10, 210, 49, 16))
        self.label_10.setObjectName("label_10")

        self.label_11 = QtWidgets.QLabel(parent=Form)
        self.label_11.setGeometry(QtCore.QRect(10, 100, 131, 21))
        self.label_11.setWordWrap(True)
        self.label_11.setObjectName("label_11")

        # --- Spinboxes ---
        self.short_delay_box = QtWidgets.QDoubleSpinBox(parent=Form)
        self.short_delay_box.setGeometry(QtCore.QRect(10, 70, 88, 23))
        self.short_delay_box.setObjectName("short_delay_box")

        self.medium_delay_box = QtWidgets.QDoubleSpinBox(parent=Form)
        self.medium_delay_box.setGeometry(QtCore.QRect(110, 70, 88, 23))
        self.medium_delay_box.setObjectName("medium_delay_box")

        # --- LineEdits ---
        self.username_box = QtWidgets.QLineEdit(parent=Form)
        self.username_box.setGeometry(QtCore.QRect(10, 140, 181, 21))
        self.username_box.setFrame(True)
        self.username_box.setObjectName("username_box")

        self.password_box = QtWidgets.QLineEdit(parent=Form)
        self.password_box.setGeometry(QtCore.QRect(10, 180, 181, 21))
        self.password_box.setObjectName("password_box")

        self.email_box = QtWidgets.QLineEdit(parent=Form)
        self.email_box.setGeometry(QtCore.QRect(10, 230, 181, 21))
        self.email_box.setObjectName("email_box")

        # --- Checkboxes ---
        self.email_checkbox = QtWidgets.QCheckBox(parent=Form)
        self.email_checkbox.setGeometry(QtCore.QRect(10, 260, 131, 20))
        self.email_checkbox.setObjectName("email_checkbox")

        self.send_checkbox = QtWidgets.QCheckBox(parent=Form)
        self.send_checkbox.setGeometry(QtCore.QRect(10, 290, 141, 20))
        self.send_checkbox.setObjectName("send_checkbox")

        # --- Image label ---
        self.label_7 = QtWidgets.QLabel(parent=Form)
        self.label_7.setGeometry(QtCore.QRect(190, 70, 191, 291))
        self.label_7.setText("")
        if get_image_path_func:
            img_path2 = get_image_path_func("image1.png")
            if img_path2:
                self.label_7.setPixmap(QtGui.QPixmap(img_path2))
                self.label_7.setScaledContents(True)
            else:
                logging.error("Naveeds image could not be loaded in UI")
        self.label_7.setObjectName("label_7")

        # --- Button ---
        self.start_button = QtWidgets.QPushButton(parent=Form)
        self.start_button.setGeometry(QtCore.QRect(110, 320, 75, 24))
        self.start_button.setObjectName("start_button")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Full Speed Ordering"))
        self.label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">"
                               "<span style=\" font-size:18pt; font-weight:700; text-decoration: underline;\">"
                               "Full Speed Ordering</span></p></body></html>")
        )
        self.label_3.setText(_translate("Form", "By Max Godfrey"))
        self.label_4.setText(
            _translate("Form", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:700; text-decoration: underline;\">Delays</span></p></body></html>")
        )
        self.label_5.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:700;\">Short Delay</span></p></body></html>"))
        self.label_6.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:700;\">Medium Delay</span></p></body></html>"))
        self.label_8.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:700;\">Username</span></p></body></html>"))
        self.label_9.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:700;\">Password</span></p></body></html>"))
        self.email_checkbox.setText(_translate("Form", "Email me the results"))
        self.label_10.setText(_translate("Form", "<html><head/><body><p><span style=\" font-weight:700;\">Email</span></p></body></html>"))
        self.send_checkbox.setText(_translate("Form", "Send results on finish"))
        self.label_11.setText(
            _translate("Form", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:700; text-decoration: underline;\">Personal Details</span></p></body></html>")
        )
        self.start_button.setText(_translate("Form", "Start"))
