# -*- coding: utf-8 -*-
'''
Created on 18 июл. 2017 г.

@author: tsema
'''
from PyQt4 import QtGui, uic
import sys

class ProgressGui(QtGui.QWidget):
    def __init__ (self, parent = None):
        super(ProgressGui, self).__init__(parent)
        
        if hasattr(sys, '_MEIPASS'):
            uic.loadUi(getattr(sys, '_MEIPASS') + "/step_millimetron_progress.ui", self) #Подгружаем графический интерфейс
        else: uic.loadUi("step_millimetron_progress.ui", self)
        
        self.move(6, 265)
        #==================================SIGNALS======================================
        self.pushButton.clicked.connect(self.abort)
        #===============================================================================
        self.flag_abt = False
    
    def abort(self):
        self.flag_abt = True