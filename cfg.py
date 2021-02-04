# -*- coding: utf-8 -*-
'''
Created on 18 июл. 2017 г.

@author: tsema
'''
ch = []         #Channel
gb = []         #groupBox
cb = []         #comboBox
pbm = []        #pushButtom motion
pbs = []        #pushButton start
pbc = []        #pushButton combine
dsb = []        #dubleSpinBox
lbl2 = []       #label2
pba = 0         #pushButtonAll
ser = 0         #serial

# переменная для храниения промежуточных настроек калибровки каналов
calibration_settings = ['2_3', '2_3', '2_3', '2_3', '2_3', '2_3', '2_3', '2_3',
                        '2_3', '2_3', '2_3', '2_3', '2_3', '2_3', '2_3', '2_3']

from PyQt4.Qt import QMessageBox
def show_err_dialog(s):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(s)
    msg.setWindowTitle("Warning!")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()