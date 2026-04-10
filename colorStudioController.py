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
import moderngl

import numpy as np
import skimage

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider
from PyQt6.QtGui import QIcon, QPixmap, QImage

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
        
# ----------------------------------------------------------------------------------
class CSLightController(CSController):
    def __init__(self, 
                 root: colorStudioModel.Scene, 
                 light: colorStudioModel.Light, 
                 widget: list, 
                 cwidget=None, 
                 cwController=None):
        super().__init__(root, light, widget, controlledWidget=cwidget)
        self._colorWheelController = cwController

    def on_position_changed(self, position_idx):
        self._scene.setImageIdx(position_idx)
        img = self._sceneRoot.render()
        for w in self._widget:
            w._update(img)

    def on_exposure_changed(self, exposure_value):
        self._scene.setExposure(exposure_value)
        img = self._sceneRoot.render()
        for w in self._widget:
            w._update(img)

    def on_color_requested(self):
        self._colorWheelController._controlledWidget.setWindowTitle("Color Wheel::"+self._scene._name)
        self._colorWheelController._scene = self._scene
# ----------------------------------------------------------------------------------
class CSAEController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def on_exposure_changed(self, exposure_value):
        self._scene.setExposure(exposure_value)
        img = self._sceneRoot.render()
        for w in self._widget:
            w._update(img)
            print("CSAEController::exposure_changed", exposure_value)

            
# ----------------------------------------------------------------------------------
class CSColorWheelController(CSController):
    def __init__(self,root,light,widget,cwidget=None):
        super().__init__(root,light,widget,controlledWidget =cwidget)

    def on_color_changed(self, color):
            if not self._scene == None:
                self._scene.setColor(color) 
                img = self._sceneRoot.render()
                
                for w in self._widget:
                    w._update(img)
# ----------------------------------------------------------------------------------
class CSSaturationController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def on_linear_saturation_changed(self, value):
        self._scene.setLinearSaturation(value)
        img = self._sceneRoot.render()
        for w in self._widget:
            w._update(img)

    def on_gamma_saturation_changed(self, value):
        self._scene.setGammaSaturation(value)
        img = self._sceneRoot.render()
        for w in self._widget:
            w._update(img)

# ----------------------------------------------------------------------------------