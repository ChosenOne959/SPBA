# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\SPBA\Work_Place\workplace.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Work_Win(object):
    def setupUi(self, Work_Win):
        Work_Win.setObjectName("Work_Win")
        Work_Win.resize(1146, 832)
        self.commandLinkButton = QtWidgets.QCommandLinkButton(Work_Win)
        self.commandLinkButton.setGeometry(QtCore.QRect(20, 10, 222, 48))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.DroneModel = QtWidgets.QGraphicsView(Work_Win)
        self.DroneModel.setGeometry(QtCore.QRect(690, 180, 261, 201))
        self.DroneModel.setObjectName("DroneModel")
        self.tabWidget = QtWidgets.QTabWidget(Work_Win)
        self.tabWidget.setGeometry(QtCore.QRect(640, 390, 371, 351))
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayoutWidget = QtWidgets.QWidget(self.tab)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 0, 361, 321))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(15)
        self.formLayout.setObjectName("formLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lineEdit)
        self.Thrust_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Thrust_SpinBox.setDecimals(6)
        self.Thrust_SpinBox.setProperty("value", 0.109919)
        self.Thrust_SpinBox.setObjectName("Thrust_SpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.Thrust_SpinBox)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lineEdit_3)
        self.Torque_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Torque_SpinBox.setDecimals(6)
        self.Torque_SpinBox.setProperty("value", 0.040164)
        self.Torque_SpinBox.setObjectName("Torque_SpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.Torque_SpinBox)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lineEdit_4)
        self.Air_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Air_SpinBox.setDecimals(6)
        self.Air_SpinBox.setProperty("value", 1.225)
        self.Air_SpinBox.setObjectName("Air_SpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.Air_SpinBox)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lineEdit_5)
        self.Revolutions_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Revolutions_SpinBox.setDecimals(6)
        self.Revolutions_SpinBox.setMaximum(6500.0)
        self.Revolutions_SpinBox.setProperty("value", 1.225)
        self.Revolutions_SpinBox.setObjectName("Revolutions_SpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.Revolutions_SpinBox)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.lineEdit_6)
        self.Diameter_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Diameter_SpinBox.setDecimals(6)
        self.Diameter_SpinBox.setProperty("value", 1.225)
        self.Diameter_SpinBox.setObjectName("Diameter_SpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.Diameter_SpinBox)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_7.setReadOnly(True)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.lineEdit_7)
        self.Height_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.Height_SpinBox.setDecimals(6)
        self.Height_SpinBox.setProperty("value", 1.225)
        self.Height_SpinBox.setObjectName("Height_SpinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.Height_SpinBox)
        self.lineEdit_8 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.lineEdit_8)
        self.MaxThrust_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.MaxThrust_SpinBox.setDecimals(6)
        self.MaxThrust_SpinBox.setProperty("value", 4.179446)
        self.MaxThrust_SpinBox.setObjectName("MaxThrust_SpinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.MaxThrust_SpinBox)
        self.lineEdit_9 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.lineEdit_9)
        self.MaxTorque_SpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.MaxTorque_SpinBox.setDecimals(6)
        self.MaxTorque_SpinBox.setProperty("value", 0.055562)
        self.MaxTorque_SpinBox.setObjectName("MaxTorque_SpinBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.MaxTorque_SpinBox)
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayoutWidget = QtWidgets.QWidget(Work_Win)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 80, 481, 661))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.Start = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.Start.setObjectName("Start")
        self.verticalLayout.addWidget(self.Start)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setEnabled(False)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.KeyboardCtrl = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.KeyboardCtrl.setEnabled(False)
        self.KeyboardCtrl.setCheckable(False)
        self.KeyboardCtrl.setDefault(True)
        self.KeyboardCtrl.setObjectName("KeyboardCtrl")
        self.verticalLayout.addWidget(self.KeyboardCtrl)
        self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setAutoRepeat(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.checkBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)

        self.retranslateUi(Work_Win)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Work_Win)

    def retranslateUi(self, Work_Win):
        _translate = QtCore.QCoreApplication.translate
        Work_Win.setWindowTitle(_translate("Work_Win", "Form"))
        self.commandLinkButton.setText(_translate("Work_Win", "back"))
        self.tabWidget.setToolTip(_translate("Work_Win", "<html><head/><body><p>params setting</p><p><br/></p></body></html>"))
        self.lineEdit.setText(_translate("Work_Win", "Thrust Co-efficient"))
        self.lineEdit_3.setText(_translate("Work_Win", "Torque Co-efficient"))
        self.lineEdit_4.setText(_translate("Work_Win", "air density"))
        self.lineEdit_5.setText(_translate("Work_Win", "max revulutions(/min)"))
        self.lineEdit_6.setText(_translate("Work_Win", "propeller diameter"))
        self.lineEdit_7.setText(_translate("Work_Win", "propeller height"))
        self.lineEdit_8.setText(_translate("Work_Win", "max thrust"))
        self.lineEdit_9.setText(_translate("Work_Win", "max torque"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Work_Win", "Rotor params"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Work_Win", "body params"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Work_Win", "kinematic"))
        self.textEdit.setPlaceholderText(_translate("Work_Win", "please start your code here!"))
        self.Start.setText(_translate("Work_Win", "Start"))
        self.pushButton.setText(_translate("Work_Win", "run"))
        self.KeyboardCtrl.setText(_translate("Work_Win", "keyboard control"))
        self.pushButton_3.setText(_translate("Work_Win", "display"))
        self.pushButton_2.setText(_translate("Work_Win", "stop"))
        self.checkBox.setText(_translate("Work_Win", "is remote"))
