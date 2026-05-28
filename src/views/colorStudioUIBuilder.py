# -*- coding: utf-8 -*-
"""
Color Studio - UI Builder (Redesigned 2026)
"""

import sys
import os
import moderngl
import numpy as np
import skimage

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QFileDialog,
    QToolButton, QSizePolicy, QFrame, QStatusBar
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

import models.colorStudioModel as colorStudioModel
import views.colorStudioWidget as colorStudioWidget
import controllers.colorStudioController as colorStudioController
import utils.colorStudioUtils as colorStudioUtils


# ------------------------------------------------------------------
# Base builder
# ------------------------------------------------------------------
class CSUIBuilder:

    uiLoadIMG  = None
    uiSaveIMG  = None
    uiAEonIMG  = None
    uiAEoffIMG = None
    uiDEIMG    = None
    uiIEIMG    = None
    uiCCIMG    = None
    template   = {}

    @staticmethod
    def setTemplate(widthScreen, heightScreen):
        control_panel_width = max(int(widthScreen * 0.22), 320)
        side_width          = min(400, max(int(widthScreen * 0.16), 240))
        available_height    = max(heightScreen - 80, 400)
        side_height         = min(400, max(int(available_height * 0.55), 220))
        scale               = min(1.0, widthScreen / 1920.0)

        CSUIBuilder.template = {
            'scale':                    scale,
            'uiRenderWidget_size':      (widthScreen - control_panel_width - side_width - 40, available_height),
            'uiColor3DWidget_size':     (side_width, side_height),
            'uiColorWheelWidget_size':  (side_width, side_height),
            'uiControlWidget_size':     (control_panel_width, available_height),
        }

    def __init__(self): pass

    @staticmethod
    def uiLoadIcon(pathUIimg=None):
        if pathUIimg is None:
            pathUIimg = './images/others/'
        CSUIBuilder.uiLoadIMG  = QIcon(pathUIimg + 'uiLoad.png')
        CSUIBuilder.uiSaveIMG  = QIcon(pathUIimg + 'uiSave.png')
        CSUIBuilder.uiAEonIMG  = QIcon(pathUIimg + 'uiAEon.png')
        CSUIBuilder.uiAEoffIMG = QIcon(pathUIimg + 'uiAEoff.png')
        CSUIBuilder.uiDEIMG    = QIcon(pathUIimg + 'uiLight_F_DE.png')
        CSUIBuilder.uiIEIMG    = QIcon(pathUIimg + 'uiLight_F_IE.png')
        CSUIBuilder.uiCCIMG    = QIcon(pathUIimg + 'uiLight_F_CC.png')


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------
def _hline():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #1a1a1a; margin: 0; padding: 0;")
    line.setFixedHeight(1)
    return line


def _section_label(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        "color:#555555; font-size:9px; font-weight:700;"
        " letter-spacing:2.5px; padding:6px 4px 2px 4px; background:transparent;"
    )
    return lbl


# ------------------------------------------------------------------
# Main builder
# ------------------------------------------------------------------
class CSUIAllBuilder(CSUIBuilder):

    def __init__(self, lightsScene):

        CSUIBuilder.uiLoadIcon()

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        self._applyStylesheet(app)

        screen = app.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            widthScreen, heightScreen = geom.width(), geom.height()
        else:
            widthScreen, heightScreen = 1280, 800

        CSUIBuilder.setTemplate(widthScreen, heightScreen)

        self._sceneRoot                = lightsScene
        self._activeLightControlLayout = None
        self._activeLightColorBtn      = None   # bouton source du dernier clic couleur
        self._lightControllers         = []

        # -------------------------------------------------------
        # Main window
        # -------------------------------------------------------
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("Color Studio")
        self._mainWindow.setMinimumSize(900, 600)
        self._mainWindow.setStyleSheet("QMainWindow { background: #2b2b2b; }")

        self._buildMenuBar()

        self._statusBar = QStatusBar()
        self._statusBar.setStyleSheet(
            "QStatusBar { background:#222222; color:#555555;"
            " border-top:1px solid #1a1a1a; font-size:11px; padding:0 8px; }"
        )
        self._statusBar.showMessage("Color Studio  —  ready")
        self._mainWindow.setStatusBar(self._statusBar)

        # -------------------------------------------------------
        # Layout: left | vline | render | vline | side
        # -------------------------------------------------------
        central = QWidget()
        central.setStyleSheet("background:#2b2b2b;")
        rootLayout = QHBoxLayout(central)
        rootLayout.setContentsMargins(0, 0, 0, 0)
        rootLayout.setSpacing(0)

        # -- Render widget first (needed by left panel wiring) --
        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Render")

        # -- Popup color wheel (unique instance, partagee) --
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None)

        # -- Panels --
        leftPanel = self._buildLeftPanel(lightsScene)
        rootLayout.addWidget(leftPanel)
        rootLayout.addWidget(self._vline())

        rightZone = self._buildRightZone(lightsScene)
        rootLayout.addWidget(rightZone, stretch=1)

        self._mainWindow.setCentralWidget(central)

        # -------------------------------------------------------
        # Initial render
        # -------------------------------------------------------
        img = lightsScene.render()
        self._renderWidget._update(img)
        try:
            self._color3DWidget._update(img)
        except Exception:
            pass

        try:
            self._mainWindow.setGeometry(0, 0, widthScreen, heightScreen)
            self._mainWindow.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        except Exception:
            pass
        self._mainWindow.showMaximized()

    # ------------------------------------------------------------------
    # Stylesheet
    # ------------------------------------------------------------------
    def _applyStylesheet(self, app):
        candidates = [
            os.path.join(os.path.dirname(__file__), 'colorStudioStyle.qss'),
            os.path.join(os.path.dirname(__file__), '..', 'colorStudioStyle.qss'),
            './colorStudioStyle.qss',
            './src/views/colorStudioStyle.qss',
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    app.setStyleSheet(f.read())
                print(f"ColorStudio: stylesheet loaded from {path}")
                return
        print("ColorStudio: no QSS found — using default Qt style")

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------
    def _buildMenuBar(self):
        menuBar = self._mainWindow.menuBar()

        fileMenu = menuBar.addMenu("File")
        loadAction = QAction("Load Image...", self._mainWindow)
        saveAction = QAction("Save Image...", self._mainWindow)
        exitAction = QAction("Exit",          self._mainWindow)
        loadAction.setShortcut("Ctrl+O")
        saveAction.setShortcut("Ctrl+S")
        exitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        loadAction.triggered.connect(self.loadImage)
        saveAction.triggered.connect(self.saveImage)
        exitAction.triggered.connect(self._mainWindow.close)

        viewMenu = menuBar.addMenu("View")
        self._toggleLeftAction  = QAction("Hide Control Panel", self._mainWindow)
        self._toggleRightAction = QAction("Hide Side Panel",    self._mainWindow)
        self._toggleLeftAction.setShortcut("Ctrl+1")
        self._toggleRightAction.setShortcut("Ctrl+2")
        viewMenu.addAction(self._toggleLeftAction)
        viewMenu.addAction(self._toggleRightAction)
        self._toggleLeftAction.triggered.connect(self._toggleLeftPanel)
        self._toggleRightAction.triggered.connect(self._toggleRightPanel)

    # ------------------------------------------------------------------
    # Left panel
    # ------------------------------------------------------------------
    def _buildLeftPanel(self, lightsScene):
        self._leftPanel = QWidget()
        self._leftPanel.setObjectName("leftPanel")
        self._leftPanel.setStyleSheet(
            "QWidget#leftPanel { background-color:#2b2b2b; border-right:1px solid #1a1a1a; }"
        )
        self._leftPanel.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0])

        outerLayout = QVBoxLayout(self._leftPanel)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.setSpacing(0)

        self._controlWidget = colorStudioWidget.CSDisplayControls()
        outerLayout.addWidget(self._controlWidget, stretch=1)

        # -- Lights --
        for light in lightsScene._lights:
            section = colorStudioWidget.CSQCollapsibleSection(
                f"  {light._name}", expanded=False
            )

            raw_color = getattr(light, "_npColorRGB", None)
            try:
                color_tuple = (float(raw_color[0]), float(raw_color[1]), float(raw_color[2]))
            except Exception:
                color_tuple = (1.0, 1.0, 1.0)

            lightControl = colorStudioWidget.CSQLightControlLayout(
                None,
                light_name=light._name,
                light_color=color_tuple
            )
            section.addLayout(lightControl)
            self._controlWidget._layout.addWidget(section)

            lightController = colorStudioController.CSLightController(
                lightsScene, light, [self._renderWidget]
            )
            lightController._colorWheelController = None
            self._lightControllers.append(lightController)

            lightControl._controller = lightController
            lightControl.exposure_changed.connect(lightController.on_exposure_changed)
            lightControl.position_changed.connect(lightController.on_position_changed)

            # Connexion du bouton couleur -> popup
            lightControl.color_requested.connect(lightController.on_color_requested)
            lightControl.color_requested.connect(
                lambda checked=False, lc=lightControl: self._openColorWheel(lc)
            )

        # -- Post-process --
        self._controlWidget._layout.addWidget(_hline())
        self._controlWidget._layout.addWidget(_section_label("Post-Processing"))

        # Auto Exposure
        ae = colorStudioModel.AE_Ymean(Ytarget=0.5, exposure=0.0)
        lightsScene.addPostProcess(ae)
        aeSection = colorStudioWidget.CSQCollapsibleSection("  Auto Exposure", expanded=True)
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        aeSection.addWidget(AE_layout)
        self._controlWidget._layout.addWidget(aeSection)
        
        self._ae_controller = colorStudioController.CSAEController(lightsScene, ae, [self._renderWidget])
        AE_layout.exposure_changed.connect(self._ae_controller.on_exposure_changed)

        # Saturation
        sat = colorStudioModel.Saturation()
        lightsScene.addPostProcess(sat)
        satSection = colorStudioWidget.CSQCollapsibleSection("  Saturation", expanded=True)
        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        satSection.addLayout(sat_layout)
        self._controlWidget._layout.addWidget(satSection)
        
        self._sat_controller = colorStudioController.CSSaturationController(lightsScene, sat, [self._renderWidget])
        sat_layout.linear_saturation_changed.connect(self._sat_controller.on_linear_saturation_changed)
        sat_layout.gamma_saturation_changed.connect(self._sat_controller.on_gamma_saturation_changed)

        self._controlWidget._layout.addStretch()
        return self._leftPanel

    # ------------------------------------------------------------------
    # Right zone: render + side panel
    # ------------------------------------------------------------------
    def _buildRightZone(self, lightsScene):
        container = QWidget()
        container.setStyleSheet("background:#2b2b2b;")
        hLayout = QHBoxLayout(container)
        hLayout.setContentsMargins(0, 0, 0, 0)
        hLayout.setSpacing(0)

        # Render
        renderContainer = QWidget()
        renderContainer.setStyleSheet("background:#1e1e1e;")
        renderLayout = QVBoxLayout(renderContainer)
        renderLayout.setContentsMargins(0, 0, 0, 0)
        renderLayout.setSpacing(0)
        renderLayout.addWidget(self._buildRenderToolbar())
        renderLayout.addWidget(self._renderWidget, stretch=1)
        hLayout.addWidget(renderContainer, stretch=1)

        hLayout.addWidget(self._vline())
        hLayout.addWidget(self._buildSidePanel(lightsScene))

        return container

    # ------------------------------------------------------------------
    # Render toolbar
    # ------------------------------------------------------------------
    def _buildRenderToolbar(self):
        toolbar = QWidget()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(
            "QWidget { background-color:#222222; border-bottom:1px solid #1a1a1a; }"
        )
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(6)

        renderLbl = QLabel("RENDER OUTPUT")
        renderLbl.setStyleSheet(
            "color:#444444; font-size:9px; font-weight:700;"
            " letter-spacing:2.5px; background:transparent;"
        )

        self._toggleLeftBtn = self._iconBtn("< Panel", "Hide/show control panel (Ctrl+1)")
        self._toggleLeftBtn.clicked.connect(self._toggleLeftPanel)
        self._toggleRightBtn = self._iconBtn("Panel >", "Hide/show side panel (Ctrl+2)")
        self._toggleRightBtn.clicked.connect(self._toggleRightPanel)

        loadBtn = self._iconBtn("Load", "Load image (Ctrl+O)")
        saveBtn = self._iconBtn("Save", "Save render (Ctrl+S)")
        loadBtn.clicked.connect(self.loadImage)
        saveBtn.clicked.connect(self.saveImage)

        layout.addWidget(self._toggleLeftBtn)
        layout.addWidget(renderLbl)
        layout.addStretch()
        layout.addWidget(loadBtn)
        layout.addWidget(saveBtn)
        layout.addWidget(self._toggleRightBtn)
        return toolbar

    def _iconBtn(self, text, tooltip=""):
        btn = QPushButton(text)
        btn.setFixedHeight(24)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background:transparent; color:#666666;
                border:1px solid #333333; border-radius:3px;
                padding:0 10px; font-size:11px; font-weight:600;
            }
            QPushButton:hover { background:#3a3a3a; color:#aaaaaa; border-color:#555555; }
            QPushButton:pressed { background:#444444; }
        """)
        return btn

    # ------------------------------------------------------------------
    # Side panel  (uniquement 3D — la roue est maintenant un popup)
    # ------------------------------------------------------------------
    def _buildSidePanel(self, lightsScene):
        self._sidePanel = QWidget()
        self._sidePanel.setObjectName("sidePanel")
        self._sidePanel.setStyleSheet(
            "QWidget#sidePanel { background-color:#272727; border-left:1px solid #1a1a1a; }"
        )

        cw, ch = CSUIBuilder.template['uiColor3DWidget_size']
        self._sidePanel.setFixedWidth(cw + 16)

        layout = QVBoxLayout(self._sidePanel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        titleBar = QWidget()
        titleBar.setFixedHeight(36)
        titleBar.setStyleSheet(
            "QWidget { background-color:#222222; border-bottom:1px solid #1a1a1a; }"
        )
        titleLayout = QHBoxLayout(titleBar)
        titleLayout.setContentsMargins(12, 0, 12, 0)
        sideLbl = QLabel("VISUALIZATION")
        sideLbl.setStyleSheet(
            "color:#444444; font-size:9px; font-weight:700;"
            " letter-spacing:2.5px; background:transparent;"
        )
        titleLayout.addWidget(sideLbl)
        titleLayout.addStretch()
        layout.addWidget(titleBar)

        # 3D chromaticity
        color3DSection = colorStudioWidget.CSQCollapsibleSection("  Chromaticity 3D", expanded=True)
        self._color3DWidget = colorStudioWidget.MyWidgetGL(
            skimage.transform.rescale(
                lightsScene.render(), 0.1, anti_aliasing=True, channel_axis=2
            ),
            True
        )
        self._color3DWidget.setFixedSize(cw, ch)
        color3DSection.addWidget(self._color3DWidget)
        layout.addWidget(color3DSection)

        # Hint pour la roue
        hintLbl = QLabel("")
        hintLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hintLbl.setStyleSheet(
            "color:#444444; font-size:11px; font-style:italic;"
            " padding:16px; background:transparent;"
        )
        layout.addWidget(hintLbl)
        layout.addStretch()

        # Color wheel controller (popup partage)
        colorWheelController = colorStudioController.CSColorWheelController(
            lightsScene,
            None,
            [self._renderWidget, self._color3DWidget],
            self._colorWheelWidget
        )
        self._colorWheelWidget._controller = colorWheelController
        self._colorWheelWidget.color_changed.connect(colorWheelController.on_color_changed)
        self._colorWheelWidget.color_changed.connect(self._onWheelColorChanged)

        for lc in self._lightControllers:
            if self._color3DWidget not in lc._widget:
                lc._widget.append(self._color3DWidget)
            lc._colorWheelController = colorWheelController

        return self._sidePanel

    # ------------------------------------------------------------------
    # Popup color wheel
    # ------------------------------------------------------------------
    def _openColorWheel(self, lightControlLayout):
        """Ouvre la roue pres du bouton couleur du panneau de controle."""
        self._activeLightControlLayout = lightControlLayout
        # Mise a jour du controleur de la roue sur la bonne lumiere
        if hasattr(self, '_colorWheelWidget') and self._colorWheelWidget._controller is not None:
            self._colorWheelWidget._controller._scene = lightControlLayout._controller._scene

        # Toggle : ouvre si fermé, ferme si déjà ouvert sur ce bouton
        self._colorWheelWidget.toggleNearWidget(lightControlLayout._ccButton)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet("color:#1a1a1a;")
        return line

    def _toggleLeftPanel(self):
        visible = not self._leftPanel.isVisible()
        self._leftPanel.setVisible(visible)
        self._toggleLeftAction.setText(
            "Hide Control Panel" if visible else "Show Control Panel"
        )
        if hasattr(self, '_toggleLeftBtn'):
            self._toggleLeftBtn.setText("< Panel" if visible else "Panel >")

    def _toggleRightPanel(self):
        visible = not self._sidePanel.isVisible()
        self._sidePanel.setVisible(visible)
        self._toggleRightAction.setText(
            "Hide Side Panel" if visible else "Show Side Panel"
        )

    def loadImage(self):
        path, _ = QFileDialog.getOpenFileName(
            self._mainWindow, "Load Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.exr);;All files (*.*)"
        )
        if not path:
            return
        try:
            imgDouble = colorStudioUtils.loadImage(path, CSUIBuilder.template.get('scale', 1.0))
        except Exception as e:
            self._statusBar.showMessage(f"Failed to load image: {e}", 5000)
            return
        for light in self._sceneRoot._lights:
            if light._ImagesArray is not None:
                light._ImagesArray._images = [imgDouble]
                light._ImagesArray._nbImage = 1
                light._ImagesArray._maxIdx  = 1
            light._imageIdx    = 0
            light._maxIdx      = 1
            light._needUpdate  = True
            light._firstUpdate = True
        img = self._sceneRoot.render()
        self._renderWidget._update(img)
        self._statusBar.showMessage(f"Loaded: {os.path.basename(path)}", 4000)

    def saveImage(self):
        path, _ = QFileDialog.getSaveFileName(
            self._mainWindow, "Save Image", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if path:
            ok  = self._renderWidget.saveImage(path)
            msg = f"Saved: {os.path.basename(path)}" if ok else "Save failed."
            self._statusBar.showMessage(msg, 4000)

    def _setActiveLightLayout(self, layout):
        self._activeLightControlLayout = layout

    def _onWheelColorChanged(self, rgb):
        if self._activeLightControlLayout is not None:
            self._activeLightControlLayout.setLightColor(rgb)