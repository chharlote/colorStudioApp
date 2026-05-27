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

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, QSplitter, QToolButton, QSizePolicy
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

    def __init__(self, lightsScene):

        # ----------------------------------------------------
        # INIT
        # ----------------------------------------------------
        CSUIBuilder.uiLoadIcon()

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        screen = app.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            widthScreen, heightScreen = geom.width(), geom.height()
        else:
            widthScreen, heightScreen = 1280, 800

        CSUIBuilder.setTemplate(widthScreen, heightScreen)

        self._sceneRoot = lightsScene
        self._activeLightControlLayout = None

        # ----------------------------------------------------
        # MAIN WINDOW
        # ----------------------------------------------------
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("Color Studio")

        central = QWidget()
        self._mainLayout = QHBoxLayout(central)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._mainLayout.setSpacing(0)

        # ====================================================
        # LEFT PANEL (FULL RESTORE)
        # ====================================================
        self._leftMenuWidget = QWidget()
        self._leftMenuLayout = QVBoxLayout(self._leftMenuWidget)
        self._leftMenuLayout.setContentsMargins(5, 5, 5, 5)
        self._leftMenuLayout.setSpacing(10)

        self._leftMenuWidget.setFixedWidth(
            CSUIBuilder.template['uiControlWidget_size'][0] + 40
        )

        # ----------------------------------------------------
        # CONTROL ROOT
        # ----------------------------------------------------
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        self._leftMenuLayout.addWidget(self._controlWidget)

        # ----------------------------------------------------
        # MAIN CONTENT for render
        # ----------------------------------------------------
        self._mainContentWidget = QWidget()
        self._mainContentLayout = QVBoxLayout(self._mainContentWidget)
        self._mainContentLayout.setContentsMargins(0, 0, 0, 0)
        self._mainContentLayout.setSpacing(0)

        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Render")
        self._mainContentLayout.addWidget(self._renderWidget)

        self._lightControllers = []

        # ----------------------------------------------------
        # LIGHTS (RESTORED COMPLET)
        # ----------------------------------------------------
        for light in lightsScene._lights:

            section = colorStudioWidget.CSQCollapsibleSection(
                f"Light: {light._name}",
                expanded=False
            )

            initial_color = getattr(light, "_color", (1, 1, 1))

            lightControl = colorStudioWidget.CSQLightControlLayout(
                None,
                light_name=light._name,
                light_color=initial_color
            )

            section.addLayout(lightControl)
            self._controlWidget._layout.addWidget(section)

            lightController = colorStudioController.CSLightController(
                lightsScene,
                light,
                [self._renderWidget]
            )

            lightController._colorWheelController = None
            self._lightControllers.append(lightController)

            lightControl._controller = lightController

            lightControl.exposure_changed.connect(
                lightController.on_exposure_changed
            )

            lightControl.color_requested.connect(
                lightController.on_color_requested
            )

            lightControl.position_changed.connect(
                lightController.on_position_changed
            )

            lightControl.color_requested.connect(
                lambda layout=lightControl:
                self._setActiveLightLayout(layout)
            )

        # ----------------------------------------------------
        # POST PROCESS (RESTORED)
        # ----------------------------------------------------
        ae = colorStudioModel.AE_Ymean(
            Ytarget=0.5,
            exposure=0.0
        )
        lightsScene.addPostProcess(ae)

        self._controlWidget._layout.addWidget(QLabel("Automatic Exposure"))

        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        self._controlWidget._layout.addWidget(AE_layout)

        ae_controller = colorStudioController.CSAEController(
            lightsScene,
            ae,
            []
        )

        AE_layout.exposure_changed.connect(
            ae_controller.on_exposure_changed
        )

        sat = colorStudioModel.Saturation()
        lightsScene.addPostProcess(sat)

        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        self._controlWidget._layout.addLayout(sat_layout)

        sat_controller = colorStudioController.CSSaturationController(
            lightsScene,
            sat,
            []
        )

        sat_layout.linear_saturation_changed.connect(
            sat_controller.on_linear_saturation_changed
        )
        sat_layout.gamma_saturation_changed.connect(
            sat_controller.on_gamma_saturation_changed
        )

        # ====================================================
        # RIGHT AREA
        # ====================================================
        rightArea = QWidget()
        rightLayout = QVBoxLayout(rightArea)
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(0)

        # ----------------------------------------------------
        # IMAGE VIEW (FIX ANTI ZOOM)
        # ----------------------------------------------------
        rightLayout.addWidget(self._mainContentWidget)

        # ----------------------------------------------------
        # BOTTOM RIGHT (3D + WHEEL)
        # ----------------------------------------------------
        self._rightMenuWidget = QWidget()
        self._rightMenuLayout = QHBoxLayout(self._rightMenuWidget)
        self._rightMenuLayout.setContentsMargins(0, 0, 0, 0)
        self._rightMenuLayout.setSpacing(10)

        rightLayout.addWidget(self._rightMenuWidget)

        # ====================================================
        # ASSEMBLY
        # ====================================================
        self._mainLayout.addWidget(self._leftMenuWidget)
        self._mainLayout.addWidget(rightArea, stretch=1)

        self._mainWindow.setCentralWidget(central)

        # ====================================================
        # 3D VIEW (FIXED addWidget bug)
        # ====================================================
        self._color3DWidget = colorStudioWidget.MyWidgetGL(
            skimage.transform.rescale(
                lightsScene.render(),
                0.1,
                anti_aliasing=True,
                channel_axis=2
            ),
            True
        )

        w, h = CSUIBuilder.template['uiColor3DWidget_size']
        self._color3DWidget.setFixedSize(w, h)

        color3DSection = colorStudioWidget.CSQCollapsibleSection("3D View", True)
        color3DSection.addWidget(self._color3DWidget)
        self._rightMenuLayout.addWidget(color3DSection)

        # ====================================================
        # COLOR WHEEL (FIXED addWidget bug)
        # ====================================================
        w, h = CSUIBuilder.template['uiColorWheelWidget_size']

        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None, w)
        self._colorWheelWidget.setFixedSize(w, h)

        colorWheelSection = colorStudioWidget.CSQCollapsibleSection("Color Wheel", True)
        colorWheelSection.addWidget(self._colorWheelWidget)
        self._rightMenuLayout.addWidget(colorWheelSection)

        # ----------------------------------------------------
        # COLOR WHEEL CONTROLLER
        # ----------------------------------------------------
        colorWheelController = colorStudioController.CSColorWheelController(
            lightsScene,
            None,
            [self._renderWidget, self._color3DWidget],
            self._colorWheelWidget
        )
        self._colorWheelWidget._controller = colorWheelController
        self._colorWheelWidget.color_changed.connect(
            colorWheelController.on_color_changed
        )
        self._colorWheelWidget.color_changed.connect(
            self._onWheelColorChanged
        )

        for lightController in self._lightControllers:
            lightController._widget.append(self._color3DWidget)
            lightController._colorWheelController = colorWheelController

        # ====================================================
        # SHOW
        # ====================================================
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

        # Ensure the main window starts maximized on the available screen area.
        try:
            self._mainWindow.setGeometry(0, 0, widthScreen, heightScreen)
            self._mainWindow.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        except Exception:
            pass
        self._mainWindow.showMaximized()

        img = lightsScene.render()
        self._renderWidget._update(img)

        try:
            self._color3DWidget._update(img)
        except Exception:
            pass
    
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

    def _setActiveLightLayout(self, layout):
        """Mark a light control layout as active for color wheel updates"""
        self._activeLightControlLayout = layout

    def _onWheelColorChanged(self, rgb):
        """Update the active light's color button when wheel color changes"""
        if self._activeLightControlLayout is not None:
            self._activeLightControlLayout.setLightColor(rgb)





# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
