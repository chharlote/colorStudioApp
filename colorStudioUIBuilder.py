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
import colorStudioWidget
import colorStudioController
import colorStudioUtils

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
class CSUIBuilder:
        # class attributes
        uiLoadIMG  	= None
        uiSaveIMG  	= None
        uiAEonIMG  	= None
        uiAEoffIMG 	= None
        uiDEIMG 	= None
        uiIEIMG 	=  None
        uiCCIMG 	=  None

        template1920x1080 = { 'scale': 0.5 ,                     \
            'uiRenderWidget_pos' : (480,30),                    \
            'uiRenderWidget_size' : (int(1920/2),int(1080/2)),  \
            # color3D widget
            'uiColor3DWidget_pos' : (1440,30),                  \
            'uiColor3DWidget_size' : (480,480),                 \
            # color wheel widget
            'uiColorWheelWidget_pos' : (1440,540),              \
            'uiColorWheelWidget_size' : (480,480),              \
            # menu/control widget
            'uiControlWidget_pos' : (0,30),                     \
            'uiControlWidget_size' : (480,0)}

        template3000x200 = { 'scale': 1,                        \
            'uiRenderWidget_pos' : (int(480*1.25),60),          \
            'uiRenderWidget_size' : (int(1920),int(1080)),      \
            # color3D widget
            'uiColor3DWidget_pos' : (3000-480,60),              \
            'uiColor3DWidget_size' : (480,480),                 \
            # color wheel widget
            'uiColorWheelWidget_pos' : (3000-480,540+60),       \
            'uiColorWheelWidget_size' : (480,480),              \
            # menu/control widget
            'uiControlWidget_pos' : (0,60),                     \
            'uiControlWidget_size' : (480,0)}

        template = template1920x1080

        # class method
        def setTemplate(widthSceen,heightScreen):
            if widthSceen == 3000 : CSUIBuilder.template = CSUIBuilder.template3000x200

        # constructor
        def __init__(self):
            pass

        # class method
        def uiLoadIcon(pathUIimg=None):
            if pathUIimg==None: pathUIimg = './images/others/'
            # window with buttons
            CSUIBuilder.uiLoadIMG  	= QIcon(pathUIimg+'uiLoad.png')
            CSUIBuilder.uiSaveIMG  	= QIcon(pathUIimg+'uiSave.png')
            CSUIBuilder.uiAEonIMG  	= QIcon(pathUIimg+'uiAEon.png')
            CSUIBuilder.uiAEoffIMG 	= QIcon(pathUIimg+'uiAEoff.png')
            CSUIBuilder.uiDEIMG 	=  QIcon(pathUIimg+'uiLight_F_DE.png')
            CSUIBuilder.uiIEIMG 	=  QIcon(pathUIimg+'uiLight_F_IE.png')
            CSUIBuilder.uiCCIMG 	=  QIcon(pathUIimg+'uiLight_F_CC.png')
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
class CSUIAllBuilder(CSUIBuilder):
    def __init__(self,lightsScene):
        # (0) load qIcon images and get screen resolution
        CSUIBuilder.uiLoadIcon()

        # (1) render Widget
        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Color Studio - RC 2019")
        x,y = CSUIBuilder.template['uiRenderWidget_pos']
        w,h = CSUIBuilder.template['uiRenderWidget_size']
        self._renderWidget.setGeometry(x,y,w,h)

        # (2) color3D widget
        self._color3DWidget = colorStudioWidget.MyWidgetGL(skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis =2 ),True)
        x,y = CSUIBuilder.template['uiColor3DWidget_pos']
        w, h = CSUIBuilder.template['uiColor3DWidget_size'] 
        self._color3DWidget.setGeometry(x,y,w,h)

        # (3) colorWheel Widget
        x,y = CSUIBuilder.template['uiColorWheelWidget_pos']
        w,h = CSUIBuilder.template['uiColorWheelWidget_size']
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None,w)
        self._colorWheelWidget.setGeometry(x,y,w,h)
        colorWheelController = colorStudioController.CSColorWheelController(lightsScene,None,[self._renderWidget,self._color3DWidget],self._colorWheelWidget)
        self._colorWheelWidget._controller = colorWheelController

        # (4) control Widget
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        x,y = CSUIBuilder.template['uiControlWidget_pos']
        w,h = CSUIBuilder.template['uiControlWidget_size']
        self._controlWidget.setGeometry(x,y,w,h)

        # (5) load/save layout to control widget
        loadSaveLayout = colorStudioWidget.CSQLoadSaveLayout(CSUIBuilder.uiLoadIMG,CSUIBuilder.uiSaveIMG)
        self._controlWidget._layout.addWidget(QLabel("Load / Save"))
        self._controlWidget._layout.addLayout(loadSaveLayout)

        # (6) light Control Layout per light
        for light in lightsScene._lights:
            self._controlWidget._layout.addWidget(QLabel("Light: "+light._name+" - control [ - | EV | + ] [light color] [light position]"))
            # set value according to light
            lightControl_layout = colorStudioWidget.CSQLightControlLayout(None, lightPosIdx=light._imageIdx)
            expoString = "{:+.2f}".format(light._exposure)
            lightControl_layout._exposureValueLabel.setText(expoString)
            self._controlWidget._layout.addLayout(lightControl_layout)
            # lightController
            lightController = colorStudioController.CSLightController(lightsScene, light, [self._renderWidget,self._color3DWidget])
            lightController._colorWheelController = colorWheelController
            lightControl_layout._controller = lightController

        # (7) post processing
        # hacking waiting to Post process in XML
        ae = colorStudioModel.AE_Ymean(Ytarget=0.5,exposure=0.0)
        lightsScene.addPostProcess(ae)
        self._controlWidget._layout.addWidget(QLabel("Automatic Exposure"))
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        self._controlWidget._layout.addLayout(AE_layout)
        ae_controller = colorStudioController.CSAEController(lightsScene,ae,[self._renderWidget,self._color3DWidget])
        AE_layout._controller = ae_controller

        sat = colorStudioModel.Saturation()
        lightsScene.addPostProcess(sat)
        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        self._controlWidget._layout.addLayout(sat_layout)
        sat_controller = colorStudioController.CSSaturationController(lightsScene,sat,[self._renderWidget,self._color3DWidget])
        sat_layout._controller = sat_controller
       # end of hack

        # (xxx) show all window
        self._renderWidget.show()
        self._controlWidget.show()
        self._color3DWidget.show()
        self._colorWheelWidget.show()

        # (end) init render
        self._renderWidget._update(lightsScene.render())




# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
