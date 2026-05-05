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

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction

import models.colorStudioModel as colorStudioModel
import views.colorStudioWidget as colorStudioWidget
import controllers.colorStudioController as colorStudioController
import utils.colorStudioUtils as colorStudioUtils

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

        template = {}

        # class method - calculates template dynamically based on screen resolution
        def setTemplate(widthScreen, heightScreen):
            """
            Generates layout template automatically based on screen resolution
            """
            # Layout widths
            control_panel_width = max(int(widthScreen * 0.22), 360)
            side_width = min(480, max(int(widthScreen * 0.20), 320))

            # Available render width
            render_width = max(int(widthScreen - control_panel_width - side_width - 60), 320)

            # Available height for stacks
            available_height = max(heightScreen - 120, 400)
            side_height = min(480, max(int((available_height - 20) / 2), 240))
            render_height = max(available_height, side_height * 2 + 20)

            # Scale factor for scene loading
            scale = min(1.0, widthScreen / 1920.0)

            CSUIBuilder.template = {
                'scale': scale,
                'uiRenderWidget_size': (render_width, render_height),
                'uiColor3DWidget_size': (side_width, side_height),
                'uiColorWheelWidget_size': (side_width, side_height),
                'uiControlWidget_size': (control_panel_width, render_height)
            }

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
# ----------------------------------------------------------------------------------
class CSUIAllBuilder(CSUIBuilder):
    def __init__(self,lightsScene):
        # (0) load qIcon images and get screen resolution
        CSUIBuilder.uiLoadIcon()

        # Create main window
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("Color Studio")

        central = QWidget()
        self._mainLayout = QHBoxLayout(central)
        self._mainLayout.setSpacing(20)

        # Left layout
        self._leftLayout = QVBoxLayout()
        self._leftLayout.setSpacing(20)
        # Right layout
        self._rightLayout = QVBoxLayout()
        self._rightLayout.setSpacing(20)

        # (1) render Widget
        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Color Studio")
        w,h = CSUIBuilder.template['uiRenderWidget_size']
        self._renderWidget.setFixedSize(w,h)
        self._leftLayout.addWidget(self._renderWidget)

        # (2) color3D widget
        self._color3DWidget = colorStudioWidget.MyWidgetGL(skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis =2 ),True)
        w, h = CSUIBuilder.template['uiColor3DWidget_size'] 
        self._color3DWidget.setFixedSize(w,h)
        self._rightLayout.addWidget(self._color3DWidget)

        # (3) colorWheel Widget
        w,h = CSUIBuilder.template['uiColorWheelWidget_size']
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None,w)
        self._colorWheelWidget.setFixedSize(w,h)
        self._rightLayout.addWidget(self._colorWheelWidget)
        colorWheelController = colorStudioController.CSColorWheelController(lightsScene,None,[self._renderWidget,self._color3DWidget],self._colorWheelWidget)
        self._colorWheelWidget._controller = colorWheelController
        self._colorWheelWidget.color_changed.connect(colorWheelController.on_color_changed)

        # (4) control Widget
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        self._controlWidget.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0])
        self._leftLayout.addWidget(self._controlWidget)

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
            lightControl_layout.exposure_changed.connect(lightController.on_exposure_changed)
            lightControl_layout.color_requested.connect(lightController.on_color_requested)
            lightControl_layout.position_changed.connect(lightController.on_position_changed)

        # (7) post processing
        # hacking waiting to Post process in XML
        ae = colorStudioModel.AE_Ymean(Ytarget=0.5,exposure=0.0)
        lightsScene.addPostProcess(ae)
        self._controlWidget._layout.addWidget(QLabel("Automatic Exposure"))
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        self._controlWidget._layout.addWidget(AE_layout)
        ae_controller = colorStudioController.CSAEController(lightsScene,ae,[self._renderWidget,self._color3DWidget])
        AE_layout._controller = ae_controller
        AE_layout.exposure_changed.connect(ae_controller.on_exposure_changed)

        sat = colorStudioModel.Saturation()
        lightsScene.addPostProcess(sat)
        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        self._controlWidget._layout.addLayout(sat_layout)
        sat_controller = colorStudioController.CSSaturationController(lightsScene,sat,[self._renderWidget,self._color3DWidget])
        sat_layout._controller = sat_controller
        
        sat_layout.linear_saturation_changed.connect(sat_controller.on_linear_saturation_changed)
        sat_layout.gamma_saturation_changed.connect(sat_controller.on_gamma_saturation_changed)
        # end of hack

        # Add layouts to main
        self._mainLayout.addLayout(self._leftLayout)
        self._mainLayout.addLayout(self._rightLayout)

        central.setLayout(self._mainLayout)
        self._mainWindow.setCentralWidget(central)

        # Menu bar
        menuBar = self._mainWindow.menuBar()
        fileMenu = menuBar.addMenu("File")
        loadAction = QAction("Load Image...", self._mainWindow)
        saveAction = QAction("Save Image...", self._mainWindow)
        exitAction = QAction("Exit", self._mainWindow)
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        loadAction.triggered.connect(self.loadImage)
        saveAction.triggered.connect(self.saveImage)
        exitAction.triggered.connect(self._mainWindow.close)

        # Resize main window to fit the generated layout
        main_width = CSUIBuilder.template['uiControlWidget_size'][0] + CSUIBuilder.template['uiRenderWidget_size'][0] + CSUIBuilder.template['uiColorWheelWidget_size'][0] + 100
        main_height = max(CSUIBuilder.template['uiRenderWidget_size'][1], CSUIBuilder.template['uiColor3DWidget_size'][1] * 2 + 20) + 100
        self._mainWindow.setMinimumSize(main_width, main_height)
        self._mainWindow.resize(main_width, main_height)

        # (xxx) show main window
        self._mainWindow.show()

        # (end) init render
        self._renderWidget._update(lightsScene.render())

    def loadImage(self):
        """Load an image file and display it in the render widget"""
        path, _ = QFileDialog.getOpenFileName(self._mainWindow, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All files (*.*)")
        if path:
            success = self._renderWidget.loadImage(path)
            if not success:
                # Could show a message box here, but for now just print
                print("Failed to load image")

    def saveImage(self):
        """Save the current render image to file"""
        path, _ = QFileDialog.getSaveFileName(self._mainWindow, "Save Image", "", "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp)")
        if path:
            success = self._renderWidget.saveImage(path)
            if not success:
                print("Failed to save image")





# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
