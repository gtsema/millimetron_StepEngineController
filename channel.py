# -*- coding: utf-8 -*-
'''
Created on 18 июл. 2017 г.

@author: tsema
'''
import cfg

class Channel:
    def __init__(self, d, parent = None):
        self.id = d
        self.enable = False
        self.combine = False
        self.units = 'step'
        self.calibration = '2_3'
        self.value = 0
        self.motion = u'→'
        
    def set_enable(self, b):
        self.ser = cfg.ser
        if b:
            try:
                self.ser.write([8 * self.id - 3])
                return True
            except BaseException:
                return False
        else:
            try:
                self.ser.write([8 * self.id - 4])
                return True
            except BaseException:
                return False

    def set_motion(self):
        self.ser = cfg.ser
        if self.motion == u'→':
            try:
                self.ser.write([8 * self.id - 6])
                return True
            except BaseException:
                return False

        elif self.motion == u'←':
            try:
                self.ser.write([8 * self.id - 5])
                return True
            except BaseException:
                return False

    def one_step(self):
        self.ser = cfg.ser
        try:
            self.ser.write([8 * self.id - 7])
            return True
        except BaseException:
            return False