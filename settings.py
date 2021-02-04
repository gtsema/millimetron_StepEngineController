# -*- coding: utf-8 -*-
'''
Created on 18 июл. 2017 г.

@author: tsema
'''

from PyQt4 import QtGui, QtCore, uic
import sys, serial, platform
import cfg

class SettingsGui(QtGui.QDialog):
    def __init__ (self, parent = None):
        super(SettingsGui, self).__init__(parent)
        if hasattr(sys, '_MEIPASS'):
            uic.loadUi(getattr(sys, '_MEIPASS') + "/step_millimetron_settings.ui", self) #Подгружаем графический интерфейс
        else: uic.loadUi("step_millimetron_settings.ui", self)
        
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint)
        
        if cfg.ch[0].units == u'μm': # восстанавливаем интерфейс окна Settings
            self.radioButton_1.setChecked(True)
            self.groupBox_3.setDisabled(False)
            self.fill_calibration_checkBox()
            
        elif cfg.ch[0].units == 'step':
            self.radioButton_2.setChecked(True)
            self.groupBox_3.setDisabled(True)
            self.fill_calibration_checkBox()
            
        #значения калибровки канала, который отображается в coomboBox_2 при открытии окна Settings
        self.spinBox_1.setValue(int(cfg.ch[0].calibration.split('_')[0]))
        self.spinBox_2.setValue(int(cfg.ch[0].calibration.split('_')[1]))
        
        self.search_COM()
        
        if type(cfg.ser) == serial.serialposix.Serial:
            self.comboBox_1.setCurrentIndex(self.comboBox_1.findText(cfg.ser.port))
        if self.comboBox_1.currentText() == '':
            self.search_COM()
        #==================================SIGNALS======================================
        self.rescanButton.clicked.connect(self.search_COM)
        
        self.buttonBox.accepted.connect(self.save_set) #кнопки 'ok' 'cancel'
        self.buttonBox.rejected.connect(self.close_set)
                
        self.comboBox_2.currentIndexChanged.connect(lambda:self.set_calibration(self.comboBox_2))
        self.spinBox_1.editingFinished.connect(lambda:self.set_calibration(self.spinBox_1))
        self.spinBox_2.editingFinished.connect(lambda:self.set_calibration(self.spinBox_2))

        self.radioButton_1.toggled.connect(lambda:self.switch_units(self.radioButton_1))
        self.radioButton_2.toggled.connect(lambda:self.switch_units(self.radioButton_2))
        #===============================================================================
        
    def fill_calibration_checkBox(self):
        self.comboBox_2.clear()
        for i in range(1, 17):
            self.comboBox_2.addItem('Ch%d' % i)
            
    def search_COM(self):
        ser = 0
        self.comboBox_1.clear()
        if platform.system() == 'Linux':
            found = False
            for i in range(10):
                try:
                    port = '/dev/ttyUSB%d' % i
                    ser = serial.Serial(port)
                    ser.close()
                    self.comboBox_1.addItem(port.split('/')[2])
                    found = True
                except BaseException:
                    pass
            if not found:
                self.comboBox_1.addItem('not detected')
        else:
            self.comboBox_1.addItem('OS error')
            
    def save_set(self):
        for i in range(16):            
            if self.radioButton_1.isChecked():                      # если в Settings выбрано 'μm'
                cfg.ch[i].units = u'μm'                             # записываем в каналы
                cfg.lbl2[i].setText(u'μm')
                cfg.dsb[i].setDecimals(0)
                cfg.dsb[i].setMaximum(500)
                
                cfg.ch[i].calibration = cfg.calibration_settings[i] # Записываем промежуточные значения калибровки в каждый канал
                cfg.dsb[i].setValue(0)                              # обнуляем value в Main
                
                x = int(cfg.ch[i].calibration.split('_')[0])        # рассчитываем шаг
                y = int(cfg.ch[i].calibration.split('_')[1])
                
                if (y/x) != 0: 
                    cfg.dsb[i].setSingleStep(y/x)
                else:
                    cfg.dsb[i].setSingleStep(1)
                
            elif self.radioButton_2.isChecked():                    # если в settings выбрано 'step'
                cfg.ch[i].units = 'step'
                cfg.lbl2[i].setText('step')
                cfg.dsb[i].setDecimals(0)
                cfg.dsb[i].setMaximum(50000)
                cfg.dsb[i].setSingleStep(1)
                
        if self.comboBox_1.currentText() == 'not detected' or self.comboBox_1.currentText() == 'OS error': #Если COM-порт не найден
            cfg.ser = 0
            
            for i in range(16):
                cfg.pbs[i].setDisabled(True)                        #Скрываем кнопки start и startAll
            cfg.pba.setDisabled(True)
                
            self.close()
        else:
            try:
                cfg.ser = serial.Serial(port = str('/dev/' + self.comboBox_1.currentText()), baudrate = 9600, bytesize = 8, stopbits = 1)
                for i in range(16):
                    cfg.pbs[i].setDisabled(False)
                    
                    if cfg.ch[i].enable: cfg.pba.setDisabled(False)
                    
                self.close()
            except BaseException:
                cfg.show_err_dialog('Please select COM port')
                self.search_COM()
                
    def close_set(self):
        for i in range(16):
            cfg.calibration_settings[i] = cfg.ch[i].calibration
            if cfg.ser == 0:
                cfg.pbs[i].setDisabled(True)
                cfg.pba.setDisabled(True)
        self.close()
        
    def switch_units(self, b):
        if b.objectName() == 'radioButton_1' and b.isChecked() == True:    
            self.groupBox_3.setDisabled(False)
        elif b.objectName() == 'radioButton_2' and b.isChecked() == True:
            self.groupBox_3.setDisabled(True)
            
    def set_calibration(self, b):
        if b.objectName() == 'comboBox_2':
            self.spinBox_1.setValue(int(cfg.calibration_settings[(int(self.comboBox_2.currentText()[2:])) - 1].split('_')[0]))
            self.spinBox_2.setValue(int(cfg.calibration_settings[(int(self.comboBox_2.currentText()[2:])) - 1].split('_')[1]))
        else:
            cfg.calibration_settings[int(self.comboBox_2.currentText()[2:]) - 1] = str(self.spinBox_1.value()) + '_' + str(self.spinBox_2.value())
                
                
                