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

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, QSplitter, QToolButton
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction
from PyQt6 import QtCore

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
        # (0) load qIcon images and initialize template from screen resolution
        CSUIBuilder.uiLoadIcon()
        # determine screen size (use existing QApplication if present)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        screen = app.primaryScreen()
        if screen is not None:
            geom = screen.availableGeometry()
            widthScreen = geom.width()
            heightScreen = geom.height()
        else:
            # fallback to a reasonable default
            widthScreen, heightScreen = 1280, 800
        CSUIBuilder.setTemplate(widthScreen, heightScreen)
        self._sceneRoot = lightsScene

        # Create main window
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("Color Studio")

        central = QWidget()
        self._mainLayout = QHBoxLayout(central)
        self._mainLayout.setSpacing(0)

        # Left-side menu for light controls
        self._leftMenuWidget = QWidget()
        self._leftMenuLayout = QVBoxLayout(self._leftMenuWidget)
        self._leftMenuLayout.setSpacing(10)
        self._leftMenuWidget.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0] + 40)
        self._leftMenuWidget.setVisible(True)

        self._toggleLeftMenuButton = QToolButton()
        self._toggleLeftMenuButton.setArrowType(QtCore.Qt.ArrowType.LeftArrow)
        self._toggleLeftMenuButton.setFixedSize(20, 50)
        self._toggleLeftMenuButton.clicked.connect(self._toggleLeftMenu)

        self._leftPanelContainer = QWidget()
        self._leftPanelLayout = QHBoxLayout(self._leftPanelContainer)
        self._leftPanelLayout.setSpacing(0)
        self._leftPanelLayout.setContentsMargins(0, 0, 0, 0)
        self._leftPanelLayout.addWidget(self._leftMenuWidget)
        self._leftPanelLayout.addWidget(self._toggleLeftMenuButton)

        # Main content widget in the center
        self._mainContentWidget = QWidget()
        self._mainContentLayout = QVBoxLayout(self._mainContentWidget)
        self._mainContentLayout.setSpacing(20)

        # Toggle button for right-side menu
        self._toggleRightMenuButton = QToolButton()
        self._toggleRightMenuButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
        self._toggleRightMenuButton.setFixedSize(20, 50)
        self._toggleRightMenuButton.clicked.connect(self._toggleRightMenu)

        # Right-side menu for 3D and color wheel
        self._rightMenuWidget = QWidget()
        self._rightMenuLayout = QVBoxLayout(self._rightMenuWidget)
        self._rightMenuLayout.setSpacing(10)
        self._rightMenuWidget.setFixedWidth(CSUIBuilder.template['uiColorWheelWidget_size'][0] + 40)
        self._rightMenuWidget.setVisible(False)

        self._rightPanelContainer = QWidget()
        self._rightPanelLayout = QHBoxLayout(self._rightPanelContainer)
        self._rightPanelLayout.setSpacing(0)
        self._rightPanelLayout.setContentsMargins(0, 0, 0, 0)
        self._rightPanelLayout.addWidget(self._toggleRightMenuButton)
        self._rightPanelLayout.addWidget(self._rightMenuWidget)

        self._mainLayout.addWidget(self._leftPanelContainer)
        self._mainLayout.addWidget(self._mainContentWidget)
        self._mainLayout.addWidget(self._rightPanelContainer)

        # (1) render Widget
        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Color Studio")
        w,h = CSUIBuilder.template['uiRenderWidget_size']
        self._renderWidget.setFixedSize(w,h)
        self._mainContentLayout.addWidget(self._renderWidget)

        # (2) color3D widget section
        self._color3DWidget = colorStudioWidget.MyWidgetGL(skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis=2), True)
        w, h = CSUIBuilder.template['uiColor3DWidget_size']
        self._color3DWidget.setFixedSize(w, h)
        color3DSection = colorStudioWidget.CSQCollapsibleSection("3D View", expanded=True)
        color3DSection.addWidget(self._color3DWidget)
        self._rightMenuLayout.addWidget(color3DSection)

        # (3) colorWheel Widget section
        w, h = CSUIBuilder.template['uiColorWheelWidget_size']
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None, w)
        self._colorWheelWidget.setFixedSize(w, h)
        colorWheelSection = colorStudioWidget.CSQCollapsibleSection("Color Wheel", expanded=True)
        colorWheelSection.addWidget(self._colorWheelWidget)
        self._rightMenuLayout.addWidget(colorWheelSection)

        colorWheelController = colorStudioController.CSColorWheelController(lightsScene, None, [self._renderWidget, self._color3DWidget], self._colorWheelWidget)
        self._colorWheelWidget._controller = colorWheelController
        self._colorWheelWidget.color_changed.connect(colorWheelController.on_color_changed)

        # Light controls sit in the left-side menu
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        self._controlWidget.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0])
        self._leftMenuLayout.addWidget(self._controlWidget)

        # (6) light Control Layout per light
        for light in lightsScene._lights:
            section = colorStudioWidget.CSQCollapsibleSection(f"Light: {light._name}", expanded=False)
            # set value according to light
            lightControl_layout = colorStudioWidget.CSQLightControlLayout(None, lightPosIdx=light._imageIdx, light_name=light._name)
            expoString = "{:+.2f}".format(light._exposure)
            lightControl_layout._exposureValueLabel.setText(expoString)
            section.addLayout(lightControl_layout)
            self._controlWidget._layout.addWidget(section)
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
        render_width = CSUIBuilder.template['uiRenderWidget_size'][0]
        render_height = CSUIBuilder.template['uiRenderWidget_size'][1]
        color3d_height = CSUIBuilder.template['uiColor3DWidget_size'][1]
        wheel_height = CSUIBuilder.template['uiColorWheelWidget_size'][1]
        total_height = max(render_height, color3d_height + wheel_height + 40)
        main_width = render_width + 50  # +50 for toggle button
        self._mainWindow.setMinimumSize(main_width, total_height + 100)
        self._mainWindow.resize(main_width, total_height + 100)

        # (xxx) show main window maximized to fit the screen
        self._mainWindow.showMaximized()

        # (end) init render
        self._renderWidget._update(lightsScene.render())

    def loadImage(self):
        """Load an image file and use it as the current scene render image."""
        path, _ = QFileDialog.getOpenFileName(self._mainWindow, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All files (*.*)")
        if not path:
            return

        try:
            imgDouble = colorStudioUtils.loadImage(path, CSUIBuilder.template.get('scale', 1.0))
        except Exception as e:
            print(f"Failed to load image: {e}")
            return

        # Replace all light input images with the newly loaded image.
        for light in self._sceneRoot._lights:
            if light._ImagesArray is not None:
                light._ImagesArray._images = [imgDouble]
                light._ImagesArray._nbImage = 1
                light._ImagesArray._maxIdx = 1
            light._imageIdx = 0
            light._maxIdx = 1
            light._needUpdate = True
            light._firstUpdate = True

        # Update the displayed render and 3D widget
        img = self._sceneRoot.render()
        self._renderWidget._update(img)
        self._color3DWidget._update(img)
        print(f"Loaded image into scene from {path}")

    def saveImage(self):
        """Save the current render image to file"""
        path, _ = QFileDialog.getSaveFileName(self._mainWindow, "Save Image", "", "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp)")
        if path:
            success = self._renderWidget.saveImage(path)
            if not success:
                print("Failed to save image")

    def _toggleLeftMenu(self):
        """Toggle the visibility of the left-side control menu."""
        if self._leftMenuWidget.isVisible():
            self._leftMenuWidget.setVisible(False)
            self._toggleLeftMenuButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
        else:
            self._leftMenuWidget.setVisible(True)
            self._toggleLeftMenuButton.setArrowType(QtCore.Qt.ArrowType.LeftArrow)

    def _toggleRightMenu(self):
        """Toggle the visibility of the right-side 3D/color wheel menu."""
        if self._rightMenuWidget.isVisible():
            self._rightMenuWidget.setVisible(False)
            self._toggleRightMenuButton.setArrowType(QtCore.Qt.ArrowType.RightArrow)
        else:
            self._rightMenuWidget.setVisible(True)
            self._toggleRightMenuButton.setArrowType(QtCore.Qt.ArrowType.LeftArrow)





# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
