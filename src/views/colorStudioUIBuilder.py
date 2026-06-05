# -*- coding: utf-8 -*-
"""
Color Studio — UI Builder (Redesigned 2026 + Theme Toggle + Async Load)
"""

import sys
import os
import traceback
import moderngl
import numpy as np
import skimage

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QFileDialog,
    QToolButton, QSizePolicy, QFrame, QStatusBar,
    QProgressBar, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import models.colorStudioModel as colorStudioModel
import views.colorStudioWidget as colorStudioWidget
import controllers.colorStudioController as colorStudioController
import utils.colorStudioUtils as colorStudioUtils
from utils.colorStudioTheme import ThemeManager


# ------------------------------------------------------------------
# Thread de chargement
# ------------------------------------------------------------------
class SceneLoaderThread(QThread):
    progress = pyqtSignal(int, int, str)   # current, total, light_name
    finished = pyqtSignal(object)          # scene
    error    = pyqtSignal(str)             # traceback

    def __init__(self, json_path, scale):
        super().__init__()
        self._json_path = json_path
        self._scale     = scale

    def run(self):
        try:
            scene = colorStudioModel.Scene()
            scene.fromJSON(
                self._json_path,
                scale=self._scale,
                progress_callback=lambda cur, tot, name:
                    self.progress.emit(cur, tot, name)
            )
            self.finished.emit(scene)
        except Exception:
            self.error.emit(traceback.format_exc())

# ------------------------------------------------------------------
# Ecrans temporaires (Accueil et Chargement)
# ------------------------------------------------------------------
class WelcomeScreen(QWidget):
    load_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(16)

        title = QLabel("Color Studio")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#777;font-size:28px;font-weight:300;letter-spacing:4px;")

        hint = QLabel("Chargez un fichier de configuration JSON\npour commencer.")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color:#666;font-size:12px;")

        btn = QPushButton("  Ouvrir un fichier JSON  ")
        btn.setFixedHeight(38)
        btn.setStyleSheet("""
            QPushButton{background:#333;color:#aaa;border:1px solid #444; border-radius:5px;font-size:13px;padding:0 24px;}
            QPushButton:hover{background:#3d3d3d;color:#ccc;border-color:#666;}
        """)
        btn.clicked.connect(self.load_requested.emit)

        lay.addStretch()
        lay.addWidget(title)
        lay.addSpacing(6)
        lay.addWidget(hint)
        lay.addSpacing(14)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addStretch()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(20,20,20,210);")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)

        self._lightLabel = QLabel("Chargement...")
        self._lightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lightLabel.setStyleSheet("color:#888;font-size:13px;background:transparent;")

        self._bar = QProgressBar()
        self._bar.setFixedWidth(320)
        self._bar.setFixedHeight(5)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        self._bar.setStyleSheet("""
            QProgressBar{background:#2a2a2a;border:none;border-radius:3px;}
            QProgressBar::chunk{background:#777;border-radius:3px;}
        """)

        self._detailLabel = QLabel("")
        self._detailLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detailLabel.setStyleSheet("color:#444;font-size:10px;font-family:Consolas,monospace;background:transparent;")

        lay.addStretch()
        lay.addWidget(self._lightLabel)
        lay.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._detailLabel)
        lay.addStretch()

    def update_progress(self, current, total, light_name):
        pct = int(current / max(total, 1) * 100)
        self._bar.setValue(pct)
        self._lightLabel.setText(f"Chargement de {light_name}...")
        self._detailLabel.setText(f"image {current + 1} / {total}")
        QApplication.processEvents()

    def resizeEvent(self, e):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(e)


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

    def __init__(self):
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

        self._sceneRoot                = None
        self._activeLightControlLayout = None
        self._activeLightColorBtn      = None
        self._lightControllers         = []
        self._loaderThread             = None

        self._appIcon = self._loadAppIcon()
        if self._appIcon:
            app.setWindowIcon(self._appIcon)
            QApplication.setWindowIcon(self._appIcon)

        # ── Fenêtre principale ──────────────────
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("Color Studio")
        if self._appIcon:
            self._mainWindow.setWindowIcon(self._appIcon)
        self._mainWindow.setMinimumSize(900, 600)

        self._buildMenuBar()

        self._statusBar = QStatusBar()
        self._statusBar.showMessage("Aucune scène chargée — File > Load JSON ou bouton Load")
        self._mainWindow.setStatusBar(self._statusBar)

        # ── Layout racine ───────────────────────
        central = QWidget()
        rootLayout = QHBoxLayout(central)
        rootLayout.setContentsMargins(0, 0, 0, 0)
        rootLayout.setSpacing(0)

        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None)

        # Panneaux vides initiaux
        self._leftPanel = self._makeEmptyLeftPanel()
        rootLayout.addWidget(self._leftPanel)
        rootLayout.addWidget(self._vline())

        self._rightZone = QWidget()
        rightLay = QHBoxLayout(self._rightZone)
        rightLay.setContentsMargins(0, 0, 0, 0)
        rightLay.setSpacing(0)

        renderContainer = QWidget()
        renderContainer.setObjectName("renderContainer")
        renderLayout = QVBoxLayout(renderContainer)
        renderLayout.setContentsMargins(0, 0, 0, 0)
        renderLayout.setSpacing(0)
        renderLayout.addWidget(self._buildRenderToolbar())

        self._stack = QWidget()
        self._stackLay = QVBoxLayout(self._stack)
        self._stackLay.setContentsMargins(0, 0, 0, 0)
        
        self._welcome = WelcomeScreen()
        self._welcome.load_requested.connect(self.loadJSON)
        self._stackLay.addWidget(self._welcome)

        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Render")
        self._renderWidget.hide()
        self._stackLay.addWidget(self._renderWidget)

        renderLayout.addWidget(self._stack, stretch=1)
        
        self._overlay = LoadingOverlay(self._stack)
        self._overlay.hide()

        rightLay.addWidget(renderContainer, stretch=1)
        rightLay.addWidget(self._vline())
        
        self._sidePanel = self._makeEmptySidePanel()
        rightLay.addWidget(self._sidePanel)

        rootLayout.addWidget(self._rightZone, stretch=1)
        self._mainWindow.setCentralWidget(central)

        try:
            self._mainWindow.setGeometry(0, 0, widthScreen, heightScreen)
            self._mainWindow.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        except Exception:
            pass
        if self._appIcon:
            self._mainWindow.setWindowIcon(self._appIcon)
        self._mainWindow.showMaximized()

        ThemeManager.instance().theme_changed.connect(self._onThemeChanged)

    # ------------------------------------------------------------------
    # Stylesheet
    # ------------------------------------------------------------------
    def _applyStylesheet(self, app):
        theme_name = ThemeManager.instance().name
        filenames = ['colorStudioStyleLight.qss'] if theme_name == 'light' else ['colorStudioStyle.qss']
        base_dirs = [
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(__file__), '..'),
            '.', './src/views', './styles',
        ]
        for fname in filenames:
            for d in base_dirs:
                path = os.path.join(d, fname)
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        app.setStyleSheet(f.read())
                    return

    def _onThemeToggle(self):
        ThemeManager.instance().toggle()

    def _onThemeChanged(self, theme_name: str):
        app = QApplication.instance()
        self._applyStylesheet(app)
        if hasattr(self, '_themeToggleBtn'):
            icon = "☀" if theme_name == 'dark' else "🌙"
            label = f"{icon} Light" if theme_name == 'dark' else f"{icon} Dark"
            self._themeToggleBtn.setText(label)
        if hasattr(self, '_toggleThemeAction'):
            self._toggleThemeAction.setText("☀  Light Theme" if theme_name == 'dark' else "🌙  Dark Theme")
        self._mainWindow.style().unpolish(self._mainWindow)
        self._mainWindow.style().polish(self._mainWindow)
        self._mainWindow.update()

    def _loadAppIcon(self):
        base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images'))
        ico_path = os.path.join(base_dir, 'colorstudiologo.ico')
        png_path = os.path.join(base_dir, 'colorstudiologo.png')
        if os.path.exists(ico_path):
            return QIcon(ico_path)
        if os.path.exists(png_path):
            return QIcon(png_path)
        return None

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------
    def _buildMenuBar(self):
        menuBar = self._mainWindow.menuBar()

        fileMenu = menuBar.addMenu("File")
        self._loadAction = QAction("Load JSON...", self._mainWindow)
        self._saveAction = QAction("Save Image...", self._mainWindow)
        exitAction = QAction("Exit", self._mainWindow)
        self._loadAction.setShortcut("Ctrl+O")
        self._saveAction.setShortcut("Ctrl+S")
        self._saveAction.setEnabled(False)
        exitAction.setShortcut("Ctrl+Q")
        
        fileMenu.addAction(self._loadAction)
        fileMenu.addAction(self._saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        
        self._loadAction.triggered.connect(self.loadJSON)
        self._saveAction.triggered.connect(self.saveImage)
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
        viewMenu.addSeparator()
        self._toggleThemeAction = QAction("☀  Light Theme", self._mainWindow)
        self._toggleThemeAction.setShortcut("Ctrl+T")
        self._toggleThemeAction.triggered.connect(self._onThemeToggle)
        viewMenu.addAction(self._toggleThemeAction)

    # ------------------------------------------------------------------
    # Render toolbar
    # ------------------------------------------------------------------
    def _buildRenderToolbar(self):
        toolbar = QWidget()
        toolbar.setObjectName("renderToolbar")
        toolbar.setFixedHeight(36)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(6)

        renderLbl = QLabel("RENDER OUTPUT")
        renderLbl.setStyleSheet("color:#444444; font-size:9px; font-weight:700; letter-spacing:2.5px; background:transparent;")

        self._toggleLeftBtn = self._iconBtn("< Panel", "Hide/show control panel (Ctrl+1)")
        self._toggleLeftBtn.clicked.connect(self._toggleLeftPanel)
        self._toggleRightBtn = self._iconBtn("Panel >", "Hide/show side panel (Ctrl+2)")
        self._toggleRightBtn.clicked.connect(self._toggleRightPanel)

        self._loadBtn = self._iconBtn("Load JSON", "Load scene config (Ctrl+O)")
        self._saveBtn = self._iconBtn("Save", "Save render (Ctrl+S)")
        self._saveBtn.setEnabled(False)
        self._loadBtn.clicked.connect(self.loadJSON)
        self._saveBtn.clicked.connect(self.saveImage)

        self._themeToggleBtn = self._iconBtn("☀ Light", "Passer au thème clair (Ctrl+T)")
        self._themeToggleBtn.clicked.connect(self._onThemeToggle)

        layout.addWidget(self._toggleLeftBtn)
        layout.addWidget(renderLbl)
        layout.addStretch()
        layout.addWidget(self._loadBtn)
        layout.addWidget(self._saveBtn)
        layout.addWidget(self._themeToggleBtn)
        layout.addWidget(self._toggleRightBtn)
        return toolbar

    def _iconBtn(self, text, tooltip=""):
        btn = QPushButton(text)
        btn.setFixedHeight(24)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton { background:transparent; color:#666666; border:1px solid #333333; border-radius:3px; padding:0 10px; font-size:11px; font-weight:600; }
            QPushButton:hover { background:#3a3a3a; color:#aaaaaa; border-color:#555555; }
            QPushButton:pressed { background:#444444; }
            QPushButton:disabled { color:#3a3a3a; border-color:#2a2a2a; }
        """)
        return btn

    # ------------------------------------------------------------------
    # Placeholders Vides
    # ------------------------------------------------------------------
    def _makeEmptyLeftPanel(self):
        p = QWidget()
        p.setObjectName("leftPanel")
        p.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0])
        lay = QVBoxLayout(p)
        lbl = QLabel("Panneau de contrôle\n(Chargez un JSON)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color:#555;")
        lay.addWidget(lbl)
        return p

    def _makeEmptySidePanel(self):
        p = QWidget()
        p.setObjectName("sidePanel")
        cw, ch = CSUIBuilder.template['uiColor3DWidget_size']
        p.setFixedWidth(cw + 16)
        lay = QVBoxLayout(p)
        lbl = QLabel("Visualisation 3D\n(Chargez un JSON)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color:#555;")
        lay.addWidget(lbl)
        return p

    # ------------------------------------------------------------------
    # Chargement JSON (Asynchrone)
    # ------------------------------------------------------------------
    def loadJSON(self):
        if self._loaderThread and self._loaderThread.isRunning():
            return
        path, _ = QFileDialog.getOpenFileName(
            self._mainWindow, "Color Studio — Ouvrir une configuration",
            "", "JSON files (*.json);;All files (*.*)"
        )
        if not path:
            return
        
        self._overlay.setGeometry(self._stack.rect())
        self._overlay._bar.setValue(0)
        self._overlay._lightLabel.setText("Initialisation...")
        self._overlay._detailLabel.setText("")
        self._overlay.show()
        self._overlay.raise_()

        self._loadBtn.setEnabled(False)
        self._loadAction.setEnabled(False)
        self._statusBar.showMessage(f"Chargement de {os.path.basename(path)}...")

        scale = CSUIBuilder.template.get('scale', 0.5)
        self._loaderThread = SceneLoaderThread(path, scale)
        self._loaderThread.progress.connect(self._overlay.update_progress)
        self._loaderThread.finished.connect(self._onLoadDone)
        self._loaderThread.error.connect(self._onLoadError)
        self._loaderThread.start()

    def _onLoadDone(self, scene):
        self._overlay.hide()
        self._loadBtn.setEnabled(True)
        self._loadAction.setEnabled(True)
        self._loaderThread = None
        self._sceneRoot = scene
        
        # Replace empty panels with actual ones
        newLeft = self._buildLeftPanel(scene)
        rl = self._mainWindow.centralWidget().layout()
        rl.replaceWidget(self._leftPanel, newLeft)
        self._leftPanel.deleteLater()
        self._leftPanel = newLeft

        self._welcome.hide()
        self._renderWidget.show()

        newSide = self._buildSidePanel(scene)
        self._rightZone.layout().replaceWidget(self._sidePanel, newSide)
        self._sidePanel.deleteLater()
        self._sidePanel = newSide

        img = scene.render()
        self._renderWidget._update(img)
        try:
            self._color3DWidget._update(img)
        except Exception: pass

        self._saveBtn.setEnabled(True)
        self._saveAction.setEnabled(True)
        self._statusBar.showMessage(f"Scène chargée — {len(scene._lights)} lumière(s)", 5000)

    def _onLoadError(self, err):
        self._overlay.hide()
        self._loadBtn.setEnabled(True)
        self._loadAction.setEnabled(True)
        self._loaderThread = None
        dlg = QMessageBox(self._mainWindow)
        dlg.setWindowTitle("Erreur de chargement")
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.setText("Impossible de charger le fichier JSON.")
        dlg.setDetailedText(err)
        dlg.exec()
        self._statusBar.showMessage("Échec du chargement.", 5000)

    # ------------------------------------------------------------------
    # Left panel (Construit après chargement)
    # ------------------------------------------------------------------
    def _buildLeftPanel(self, lightsScene):
        panel = QWidget()
        panel.setObjectName("leftPanel")
        panel.setFixedWidth(CSUIBuilder.template['uiControlWidget_size'][0])

        outerLayout = QVBoxLayout(panel)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.setSpacing(0)

        self._controlWidget = colorStudioWidget.CSDisplayControls()
        outerLayout.addWidget(self._controlWidget, stretch=1)
        self._lightControllers = []

        for light in lightsScene._lights:
            section = colorStudioWidget.CSQCollapsibleSection(f"  {light._name}", expanded=False)
            raw_color = getattr(light, "_npColorRGB", None)
            try: color_tuple = (float(raw_color[0]), float(raw_color[1]), float(raw_color[2]))
            except Exception: color_tuple = (1.0, 1.0, 1.0)

            lightControl = colorStudioWidget.CSQLightControlLayout(None, light_name=light._name, light_color=color_tuple)
            section.addLayout(lightControl)
            self._controlWidget._layout.addWidget(section)

            lightController = colorStudioController.CSLightController(lightsScene, light, [self._renderWidget])
            lightController._colorWheelController = None
            self._lightControllers.append(lightController)

            lightControl._controller = lightController
            lightControl.exposure_changed.connect(lightController.on_exposure_changed)
            lightControl.position_changed.connect(lightController.on_position_changed)
            lightControl.color_requested.connect(lightController.on_color_requested)
            lightControl.color_requested.connect(lambda checked=False, lc=lightControl: self._openColorWheel(lc))

        self._controlWidget._layout.addWidget(_hline())
        self._controlWidget._layout.addWidget(_section_label("Post-Processing"))

        ae = colorStudioModel.AE_Ymean(Ytarget=0.5, exposure=0.0)
        lightsScene.addPostProcess(ae)
        aeSection = colorStudioWidget.CSQCollapsibleSection("  Auto Exposure", expanded=True)
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        aeSection.addWidget(AE_layout)
        self._controlWidget._layout.addWidget(aeSection)

        self._ae_controller = colorStudioController.CSAEController(lightsScene, ae, [self._renderWidget])
        AE_layout.exposure_changed.connect(self._ae_controller.on_exposure_changed)

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
        return panel

    # ------------------------------------------------------------------
    # Side panel (Construit après chargement)
    # ------------------------------------------------------------------
    def _buildSidePanel(self, lightsScene):
        panel = QWidget()
        panel.setObjectName("sidePanel")
        cw, ch = CSUIBuilder.template['uiColor3DWidget_size']
        panel.setFixedWidth(cw + 16)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titleBar = QWidget()
        titleBar.setObjectName("sideTitleBar")
        titleBar.setFixedHeight(36)
        titleLayout = QHBoxLayout(titleBar)
        titleLayout.setContentsMargins(12, 0, 12, 0)
        sideLbl = QLabel("VISUALIZATION")
        sideLbl.setStyleSheet("color:#444444; font-size:9px; font-weight:700; letter-spacing:2.5px; background:transparent;")
        titleLayout.addWidget(sideLbl)
        titleLayout.addStretch()
        layout.addWidget(titleBar)

        color3DSection = colorStudioWidget.CSQCollapsibleSection("  Chromaticity 3D", expanded=True)
        self._color3DWidget = colorStudioWidget.MyWidgetGL(
            skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis=2), True
        )
        self._color3DWidget.setFixedSize(cw, ch)
        color3DSection.addWidget(self._color3DWidget)
        layout.addWidget(color3DSection)
        layout.addStretch()

        colorWheelController = colorStudioController.CSColorWheelController(
            lightsScene, None, [self._renderWidget, self._color3DWidget], self._colorWheelWidget
        )
        self._colorWheelWidget._controller = colorWheelController
        self._colorWheelWidget.color_changed.connect(colorWheelController.on_color_changed)
        self._colorWheelWidget.color_changed.connect(self._onWheelColorChanged)

        for lc in self._lightControllers:
            if self._color3DWidget not in lc._widget:
                lc._widget.append(self._color3DWidget)
            lc._colorWheelController = colorWheelController

        return panel

    # ------------------------------------------------------------------
    # Actions & Helpers
    # ------------------------------------------------------------------
    def _openColorWheel(self, lightControlLayout):
        self._activeLightControlLayout = lightControlLayout
        if hasattr(self, '_colorWheelWidget') and self._colorWheelWidget._controller is not None:
            self._colorWheelWidget._controller._scene = lightControlLayout._controller._scene
        self._colorWheelWidget.toggleNearWidget(lightControlLayout._ccButton)

    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet("color:#1a1a1a;")
        return line

    def _toggleLeftPanel(self):
        visible = not self._leftPanel.isVisible()
        self._leftPanel.setVisible(visible)
        self._toggleLeftAction.setText("Hide Control Panel" if visible else "Show Control Panel")
        if hasattr(self, '_toggleLeftBtn'): self._toggleLeftBtn.setText("< Panel" if visible else "Panel >")

    def _toggleRightPanel(self):
        visible = not self._sidePanel.isVisible()
        self._sidePanel.setVisible(visible)
        self._toggleRightAction.setText("Hide Side Panel" if visible else "Show Side Panel")

    def saveImage(self):
        path, _ = QFileDialog.getSaveFileName(self._mainWindow, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
        if path:
            ok  = self._renderWidget.saveImage(path)
            msg = f"Saved: {os.path.basename(path)}" if ok else "Save failed."
            self._statusBar.showMessage(msg, 4000)

    def _onWheelColorChanged(self, rgb):
        if self._activeLightControlLayout is not None:
            self._activeLightControlLayout.setLightColor(rgb)