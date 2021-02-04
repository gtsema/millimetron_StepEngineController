# -*- coding: utf-8 -*-
'''
Created on 18 июл. 2017 г.

@author: tsema
'''
from PyQt4 import QtGui, uic
from PyQt4.Qt import QApplication

import sys, functools, time

import settings, progress, channel

import cfg

class MainGui(QtGui.QMainWindow):
    def __init__ (self, parent = None):
        super(MainGui, self).__init__(parent)
        if hasattr(sys, '_MEIPASS'):
            uic.loadUi(getattr(sys, '_MEIPASS') + "/step_millimetron.ui", self) #Подгружаем графический интерфейс
        else: uic.loadUi("step_millimetron.ui", self)        
        
        cfg.ch = [channel.Channel(i, self) for i in range(1, 17)]               #Список с ссылками на экземпляры каналов
        
        cfg.gb = [elem for elem in dir(self) if elem.startswith('groupBox')]    #Список groupBox'ов формы main 
        cfg.gb.sort(key = lambda x: int(x.split('_')[1]))                       #Сортируем по возрастанию 1-16
        
        cfg.cb = [elem for elem in dir(self) if elem.startswith('checkBox')]
        cfg.cb.sort(key = lambda x: int(x.split('_')[1]))
        
        cfg.pbm = [elem for elem in dir(self) if elem.startswith('pushButton_m')]
        cfg.pbm.sort(key = lambda x: int(x.split('_m')[1]))
        
        cfg.pbs = [elem for elem in dir(self) if elem.startswith('pushButton_s')]
        cfg.pbs.sort(key = lambda x: int(x.split('_s')[1]))
        
        cfg.dsb = [elem for elem in dir(self) if elem.startswith('doubleSpinBox')]
        cfg.dsb.sort(key = lambda x: int(x.split('_')[1]))
        
        cfg.pbc = [elem for elem in dir(self) if elem.startswith('pushButton') and elem.endswith('_c')]
        cfg.pbc.sort(key = lambda x: int(x.split('pushButton')[1].split('_c')[0]))
        
        cfg.lbl2 = [elem for elem in dir(self) if elem.startswith('label') and elem.endswith('2')]
        cfg.lbl2.sort(key = lambda x: int(x.split('label')[1].split('_2')[0]))
        
        for i in range(16):
            cfg.gb.insert(i, getattr(self, cfg.gb.pop(i)))                      #Заменяем имя элемента на ссылку на объект
            cfg.cb.insert(i, getattr(self, cfg.cb.pop(i)))
            cfg.pbm.insert(i, getattr(self, cfg.pbm.pop(i)))
            cfg.pbs.insert(i, getattr(self, cfg.pbs.pop(i)))
            cfg.dsb.insert(i, getattr(self, cfg.dsb.pop(i)))
            cfg.pbc.insert(i, getattr(self, cfg.pbc.pop(i)))
            cfg.lbl2.insert(i, getattr(self, cfg.lbl2.pop(i)))
        cfg.pba = getattr(self, 'pushButtonAll')
        
        #==================================SIGNALS======================================
        self.settingsButton.clicked.connect(self.settings_show)
        cfg.pba.clicked.connect(self.start_all)
                        
        for i in range(16):
            cfg.pbm[i].clicked.connect(functools.partial(self.motion_select, cfg.pbm[i]))
            cfg.pbs[i].clicked.connect(functools.partial(self.start, cfg.pbs[i]))
            cfg.cb[i].stateChanged.connect(functools.partial(self.ch_select, cfg.cb[i]))
            cfg.pbc[i].clicked.connect(functools.partial(self.combine, cfg.pbc[i]))
            cfg.dsb[i].valueChanged.connect(functools.partial(self.set_combine_value, cfg.dsb[i]))
        #===============================================================================

    def settings_show(self):
        settingsGui = settings.SettingsGui(self)
        settingsGui.move(app.desktop().screenGeometry().width()//2, app.desktop().screenGeometry().height()//4)
        settingsGui.show()
        
    def combine(self, b):
        ch_num = int(b.objectName().split('pushButton')[1].split('_c')[0]) - 1
        if cfg.ch[ch_num].combine:
            cfg.ch[ch_num].combine = False
            b.setStyleSheet("""QPushButton{ background-color: white; border-style: solid; font: bold italic "Ubuntu"; }""")
        else:
            cfg.ch[ch_num].combine = True
            b.setStyleSheet("""QPushButton{ background-color: rgb(240, 200, 174); border-style: solid; font: bold italic "Ubuntu"; }""")
    
    def set_combine_value(self, b):
        if cfg.ch[int(b.objectName().split('_')[1]) - 1].combine:
            for i in range(16):
                if cfg.ch[i].combine:
                    cfg.dsb[i].setValue(b.value()) 
     
    def motion_select(self, b):
        if b.isChecked():
            b.setText(u'←')
            cfg.ch[cfg.pbm.index(b)].motion = u'←'
        else:
            b.setText(u'→')
            cfg.ch[cfg.pbm.index(b)].motion = u'→'
        
    def ch_select(self, b):
        if b.checkState() == 2:
            cfg.gb[cfg.cb.index(b)].setDisabled(False)
            cfg.ch[cfg.cb.index(b)].enable = True
            cfg.pba.setDisabled(False)
            
            if type(cfg.ser) == int:
                cfg.pbs[cfg.cb.index(b)].setDisabled(True)
                cfg.pba.setDisabled(True)
        else:
            cfg.gb[cfg.cb.index(b)].setDisabled(True)
            cfg.ch[cfg.cb.index(b)].enable = False
            
            x = False
            for i in range(16):
                x = x or cfg.ch[i].enable
            if not x: cfg.pba.setDisabled(True)
            
    def writing_values(self, b):
        if b != 0 and cfg.ch[0].units == 'step': # step + start
            cfg.ch[cfg.pbs.index(b)].value = cfg.dsb[cfg.pbs.index(b)].value()
                        
        elif b == 0 and cfg.ch[0].units == 'step': # step + startAll
            for i in range(16):
                if cfg.ch[i].enable == 1 and cfg.dsb[i].value() != 0:
                    cfg.ch[i].value = int(cfg.dsb[i].value())

        elif b != 0 and cfg.ch[0].units == u'μm': # μm + start
            x = float(cfg.ch[cfg.pbs.index(b)].calibration.split('_')[0])
            y = float(cfg.ch[cfg.pbs.index(b)].calibration.split('_')[1])
            val = cfg.dsb[cfg.pbs.index(b)].value()
            
            if round(val % (y/x), 2) == 0:
                cfg.ch[cfg.pbs.index(b)].value = int(val/(y/x))
            else:
                val_min = (y/x) * (val // (y/x))
                val_max = val_min + (y/x)
                if val_max - val < val - val_min:
                    val = int(val_max / (y/x))
                else:
                    val = int(val_min / (y/x))
                                
                cfg.ch[cfg.pbs.index(b)].value = val
                cfg.dsb[cfg.pbs.index(b)].setValue(val*(y/x))
        
        elif b == 0 and cfg.ch[0].units == u'μm': # μm + startAll
            for i in range(16):
                if cfg.ch[i].enable == 1 and cfg.dsb[i].value() != 0:
                    x = float(cfg.ch[i].calibration.split('_')[0])
                    y = float(cfg.ch[i].calibration.split('_')[1])
                    val = cfg.dsb[i].value()
                    
                    if round(val % (y/x), 2) == 0:
                        cfg.ch[i].value = int(val/(y/x))
                    else:
                        val_min = (y/x) * (val // (y/x))
                        val_max = val_min + (y/x)
                        
                        if val_max - val < val - val_min:
                            val = int(val_max / (y/x))  
                        else:
                            val = int(val_min / (y/x))
   
                        cfg.ch[i].value = val
                        cfg.dsb[i].setValue(val*(y/x))
                        
    def start(self, b):
        self.centralwidget.setDisabled(True)
        self.writing_values(b)
        ch_val = int(cfg.ch[cfg.pbs.index(b)].value)
        
        if ch_val > 100000: cfg.show_err_dialog('Over 100k steps!')
        
        if not cfg.ch[cfg.pbs.index(b)].set_enable(True):
            cfg.show_err_dialog('Please select COM port')
            self.centralwidget.setDisabled(False)
            self.settings_show()
            return
        if not cfg.ch[cfg.pbs.index(b)].set_motion():
            cfg.show_err_dialog('Please select COM port')
            self.centralwidget.setDisabled(False)
            self.settings_show()
            return
        
        progressGui = progress.ProgressGui(self)
        progressGui.show()
        
        progressGui.progressBar.setMaximum(ch_val)
        
        #start = time.time()
        
        for i in range(int(ch_val)):
            if not progressGui.flag_abt:
                if cfg.ch[1].one_step():
                    time.sleep(0.0005)
                    progressGui.progressBar.setValue(i)
                    if i % 3 == 0:
                        QApplication.processEvents()
                else:
                    cfg.show_err_dialog('Please select COM port')
                    self.centralwidget.setDisabled(False)
                    self.settings_show()
                    break
            else: break
        #stop = time.time()
        
        progressGui.close()
        self.centralwidget.setDisabled(False)
        
        #print round(stop - start, 2)
    
    def start_all(self):
        self.centralwidget.setDisabled(True)
        self.writing_values(0)
        summ = 0
        for i in range(16):
            if cfg.ch[i].enable == 1 and cfg.ch[i].value != 0:
                
                if not cfg.ch[i].set_enable(True):
                    cfg.show_err_dialog('Please select COM port')
                    self.centralwidget.setDisabled(False)
                    self.settings_show()
                    return
                if not cfg.ch[i].set_motion():
                    cfg.show_err_dialog('Please select COM port')
                    self.centralwidget.setDisabled(False)
                    self.settings_show()
                    return
                
                summ += int(cfg.ch[i].value)
        
        if summ > 100000: cfg.show_err_dialog('Over 100k steps!')
        
        progressGui = progress.ProgressGui(self)
        progressGui.show()
        progressGui.progressBar.setMaximum(summ)

        while summ != 0 and not progressGui.flag_abt:
            for i in range(16):
                if cfg.ch[i].enable == 1 and cfg.ch[i].value != 0:
                    if cfg.ch[i].one_step():
                        time.sleep(0.0005)
                        cfg.ch[i].value -= 1
                        progressGui.progressBar.setValue(int(progressGui.progressBar.maximum()) - summ)
                        summ -= 1
                        if summ % 3 == 0:
                            QApplication.processEvents()
                    else:
                        cfg.show_err_dialog('Please select COM port')
                        self.centralwidget.setDisabled(False)
                        self.settings_show()
                        break
            
        progressGui.close()
        self.centralwidget.setDisabled(False)
  
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainGui = MainGui()
    mainGui.move(app.desktop().screenGeometry().width()//4, app.desktop().screenGeometry().height()//4)
    mainGui.show()
    mainGui.settings_show()
    sys.exit(app.exec_())