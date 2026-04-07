# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""
# ----------------------------------------------------------------------------------
# main changes
# ----------------------------------------------------------------------------------
# GUI lib: pygame to pyqt5
# include 3d color point cloud (modernGL) 
# ----------------------------------------------------------------------------------
# version0.0
# -----------------------------------------------------------------------------------
# Qt window

# import(s)
# ----------------------------------------------------------------------------------

import sys
import imageio
import moderngl

import numpy as np
import skimage

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5 import QtCore, QtOpenGL 

import colorStudioModel

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

class CSController:
    def __init__(self, root = None, scene=None, widget=None , controlledWidget = None):
        # attributes
        # controlledWidget
        self._controlledWidget = controlledWidget
        # sceneRoot
        self._sceneRoot = root
        # scene compoment controlled
        self._scene = scene
        # widget update after sceneRoot.render()
        self._widget = widget
    # methods
    # event method called by widget
    def _event(self,widget,event):
        pass
# ----------------------------------------------------------------------------------
class CSLightController(CSController):
    def __init__(self,root,light,widget,cwidget=None, cwController = None):
        super().__init__(root,light,widget, controlledWidget =cwidget)
        self._colorWheelController = cwController

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : slider position
        # -1 : decrease Expoosure
        # +1 : increase exposure
        # +2 : change light color

        if eventType == 0 :
            # change light position index
            self._scene.setImageIdx(event[1])  #event[1] slider position 
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)

        if eventType == 2 :
            # tell colorWheel controller that self._scene is active light
            self._colorWheelController._controlledWidget.setWindowTitle("Color Wheel::"+self._scene._name)
            self._colorWheelController._scene =  self._scene

        if eventType == -1 or eventType == 1: 
            # change light exposure
            self._scene.setExposure(event[1]) #event[1] exposure value
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)
# ----------------------------------------------------------------------------------
class CSAEController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : on off
        # -1 : decrease Expoosure
        # +1 : increase exposure

        if eventType == 0 :
            # turn on off automatic exposure
            self._scene.setOnOff(event[1])  #event[1] on/off value 
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)

        if eventType == -1 or eventType == 1: 
            # change automtic exposure  value
            self._scene.setExposure(event[1]) #event[1] exposure value
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)
# ----------------------------------------------------------------------------------
class CSColorWheelController(CSController):
    def __init__(self,root,light,widget,cwidget=None):
        super().__init__(root,light,widget,controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0 : change color

        if eventType == 0 :
            # change light color
            if not self._scene == None:
                self._scene.setColor(event[1])  #event[1] color in RGB
                # render scene
                img = self._sceneRoot.render()
                # send new image to widget(s)
                for w in self._widget:
                    w._update(img)
# ----------------------------------------------------------------------------------
class CSSaturationController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : set linear saturation 
        # 1  : set gamma saturation 

        if eventType == 0 :
            # set linear saturation
            self._scene.setLinearSaturation(event[1])  #event[1] saturation value 
        if eventType == 1 :
            # set gamma saturation
            self._scene.setGammaSaturation(event[1])  #event[1] saturation value        # render scene
        img = self._sceneRoot.render()
        # send new image to widget(s)
        for w in self._widget:
            w._update(img)

# ----------------------------------------------------------------------------------