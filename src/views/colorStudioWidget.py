# -*- coding: utf-8 -*-
"""
Color Studio — Widget Module (Redesigned UI — 2026)
"""

import sys
import imageio
import moderngl
import math
import numpy as np
import skimage

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QToolButton,
    QSizePolicy, QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QSurfaceFormat, QColor, QFont, QPainter, QPen, QBrush
)
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import models.colorStudioModel as colorStudioModel
import utils.colorStudioUtils as colorStudioUtils
import views.colorStudioUIBuilder as colorStudioUIBuilder

# ─────────────────────────────────────────────
# Screen size helper
# ─────────────────────────────────────────────
def getScreenSize():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    x, y = size.width(), size.height()
    app.quit()
    return (x, y)


# ─────────────────────────────────────────────
# OpenGL base widget
# ─────────────────────────────────────────────
class QModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setSamples(4)
        self.timer = QtCore.QElapsedTimer()

    def initializeGL(self): pass

    def paintGL(self):
        self.ctx = moderngl.create_context()
        self.screen = self.ctx.detect_framebuffer()
        self.init()
        self.render()
        self.paintGL = self.render

    def init(self): pass
    def render(self): pass


# ─────────────────────────────────────────────
# 2D GL scene helper
# ─────────────────────────────────────────────
class HelloWorld2D:
    def __init__(self, ctx, reserve='1024MB'):
        self.ctx = ctx
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform vec2 Pan;
                in vec2 in_vert;
                in vec4 in_color;
                out vec4 v_color;
                void main() {
                    v_color = in_color;
                    gl_Position = vec4(in_vert - Pan, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                in vec4 v_color;
                out vec4 f_color;
                void main() {
                    f_color = v_color;
                }
            ''',
        )
        self.vbo = ctx.buffer(reserve='1024MB', dynamic=True)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

    def pan(self, pos):
        self.prog['Pan'].value = pos

    def clear(self, color=(0, 0, 0, 0)):
        self.ctx.clear(*color)

    def plot(self, points, type='points'):
        data = points.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        if type == 'line':
            self.ctx.line_width = 1.0
            self.vao.render(moderngl.LINE_STRIP, vertices=len(data) // 24)
        if type == 'points':
            self.ctx.point_size = 3.0
            self.vao.render(moderngl.POINTS, vertices=len(data) // 24)


# ─────────────────────────────────────────────
# Pan helper
# ─────────────────────────────────────────────
class PanTool:
    def __init__(self):
        self.total_x = self.total_y = 0.0
        self.start_x = self.start_y = 0.0
        self.delta_x = self.delta_y = 0.0
        self.drag = False

    def start_drag(self, x, y):
        self.start_x, self.start_y = x, y
        self.drag = True

    def dragging(self, x, y):
        if self.drag:
            self.delta_x = (x - self.start_x) * 2.0
            self.delta_y = (y - self.start_y) * 2.0

    def stop_drag(self, x, y):
        if self.drag:
            self.dragging(x, y)
            self.total_x -= self.delta_x
            self.total_y += self.delta_y
            self.delta_x = self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)


pan_tool = PanTool()


# ─────────────────────────────────────────────
# 3D chromaticity viewer
# ─────────────────────────────────────────────
class MyWidgetGL(QModernGLWidget):
    def __init__(self, img, scene=None):
        super().__init__()
        self.VBOdata = colorStudioUtils.img2chromaVertices(img, False)
        self.setWindowTitle("3D Color")

    def init(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.scene = HelloWorld2D(self.ctx)

    def resizeGL(self, w, h):
        if hasattr(self, 'ctx'):
            self.ctx.viewport = (0, 0, w, h)

    def render(self):
        self.screen.use()
        self.scene.clear()
        self.scene.plot(self.VBOdata)

    def mousePressEvent(self, evt):
        pan_tool.start_drag(evt.position().x() / 512, evt.position().y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseMoveEvent(self, evt):
        pan_tool.dragging(evt.position().x() / 512, evt.position().y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseReleaseEvent(self, evt):
        pan_tool.stop_drag(evt.position().x() / 512, evt.position().y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def _update(self, img):
        self.VBOdata = colorStudioUtils.img2chromaVertices(img, False)
        self.update()

    def saveImage(self, path):
        pixmap = self.grab()
        return pixmap.save(path)


# ─────────────────────────────────────────────
# Collapsible Section  (redesigned)
# ─────────────────────────────────────────────
class CSQCollapsibleSection(QWidget):

    def __init__(self, title, expanded=False, parent=None):
        super().__init__(parent)
        self.setObjectName("collapsibleSection")

        # ── Toggle button ──────────────────────
        self._toggleButton = QToolButton()
        self._toggleButton.setText(f"  {title}")
        self._toggleButton.setCheckable(True)
        self._toggleButton.setChecked(expanded)
        self._toggleButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggleButton.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self._toggleButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggleButton.setMinimumHeight(36)
        self._toggleButton.clicked.connect(self._on_toggle)

        # ── Content area ──────────────────────
        self._content = QWidget()
        self._content.setObjectName("sectionContent")
        self._content.setStyleSheet("""
            QWidget#sectionContent {
                background-color: #1a1a35;
                border-left: 2px solid #3a3a7a;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }
        """)
        self._contentLayout = QVBoxLayout(self._content)
        self._contentLayout.setContentsMargins(12, 8, 8, 10)
        self._contentLayout.setSpacing(8)
        self._content.setVisible(expanded)

        # ── Outer layout ──────────────────────
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 2)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._toggleButton)
        self._layout.addWidget(self._content)

    def _on_toggle(self):
        expanded = self._toggleButton.isChecked()
        self._toggleButton.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self._content.setVisible(expanded)

    def addWidget(self, widget):
        self._contentLayout.addWidget(widget)

    def addLayout(self, layout):
        self._contentLayout.addLayout(layout)


# ─────────────────────────────────────────────
# Light Control Layout  (redesigned)
# ─────────────────────────────────────────────
class CSQLightControlLayout(QVBoxLayout):

    exposure_changed = pyqtSignal(float)
    color_requested  = pyqtSignal()
    position_changed = pyqtSignal(int)

    def __init__(self, controller, uiDEIMG=None, uiIEIMG=None, uiCCIMG=None,
                 stepE=0.2, maxE=5, lightPosIdx=50,
                 light_name=None, light_color=None):
        super().__init__()
        self._controller   = controller
        self._step         = stepE
        self._max          = maxE
        self._exposure     = 0.0
        self._light_color  = light_color if light_color is not None else (1.0, 1.0, 1.0)
        name = light_name or "Light"

        self.setSpacing(10)
        self.setContentsMargins(0, 4, 0, 4)

        # ── Exposure row ──────────────────────
        expRow = QHBoxLayout()
        expRow.setSpacing(6)

        expLbl = QLabel("Exposure")
        expLbl.setFixedWidth(66)
        expLbl.setStyleSheet("color: #8888aa; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")

        self._deButton = QPushButton("−")   # U+2212 minus sign — visually cleaner
        self._deButton.setFixedSize(30, 30)
        self._deButton.setToolTip(f"{name}: Decrease exposure")
        self._deButton.setStyleSheet(self._btn_style())

        self._exposureValueLabel = QLabel("+0.00")
        self._exposureValueLabel.setFixedWidth(54)
        self._exposureValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._exposureValueLabel.setObjectName("exposureValue")
        self._exposureValueLabel.setStyleSheet("""
            QLabel {
                background-color: #0f0f22;
                color: #a89cf7;
                border: 1px solid #3a3a6a;
                border-radius: 4px;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 12px;
                font-weight: 600;
                padding: 2px 0;
            }
        """)

        self._ieButton = QPushButton("+")
        self._ieButton.setFixedSize(30, 30)
        self._ieButton.setToolTip(f"{name}: Increase exposure")
        self._ieButton.setStyleSheet(self._btn_style(accent=True))

        expRow.addWidget(expLbl)
        expRow.addWidget(self._deButton)
        expRow.addWidget(self._exposureValueLabel)
        expRow.addWidget(self._ieButton)
        expRow.addStretch()
        self.addLayout(expRow)

        # ── Color row ─────────────────────────
        colorRow = QHBoxLayout()
        colorRow.setSpacing(8)

        colorLbl = QLabel("Color")
        colorLbl.setFixedWidth(66)
        colorLbl.setStyleSheet("color: #8888aa; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")

        self._ccButton = QPushButton()
        self._ccButton.setFixedSize(40, 26)
        self._ccButton.setToolTip(f"{name}: Pick color from wheel")
        self._updateColorButton(self._light_color)

        self._colorHexLabel = QLabel(self._rgb_to_hex(self._light_color))
        self._colorHexLabel.setStyleSheet("""
            color: #6666aa;
            font-family: 'Consolas', monospace;
            font-size: 11px;
        """)

        colorRow.addWidget(colorLbl)
        colorRow.addWidget(self._ccButton)
        colorRow.addWidget(self._colorHexLabel)
        colorRow.addStretch()
        self.addLayout(colorRow)

        # ── Position row ──────────────────────
        posRow = QHBoxLayout()
        posRow.setSpacing(8)

        posLbl = QLabel("Position")
        posLbl.setFixedWidth(66)
        posLbl.setStyleSheet("color: #8888aa; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")

        self._sliderPosition = QSlider(Qt.Orientation.Horizontal)
        self._sliderPosition.setValue(lightPosIdx)
        self._sliderPosition.setToolTip(f"{name}: Light position on trajectory")
        self._sliderPosition.setCursor(Qt.CursorShape.PointingHandCursor)

        self._posValueLabel = QLabel(str(lightPosIdx))
        self._posValueLabel.setFixedWidth(28)
        self._posValueLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._posValueLabel.setStyleSheet("color: #6666aa; font-size: 11px;")

        posRow.addWidget(posLbl)
        posRow.addWidget(self._sliderPosition)
        posRow.addWidget(self._posValueLabel)
        self.addLayout(posRow)

        # ── Divider ───────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #2a2a4a; margin: 2px 0;")
        self.addWidget(line)

        # ── Signals ───────────────────────────
        self._ieButton.clicked.connect(self.incExposure)
        self._deButton.clicked.connect(self.decExposure)
        self._ccButton.clicked.connect(self.setColor)
        self._sliderPosition.valueChanged.connect(self._onPositionChanged)

    # ── Private helpers ───────────────────────

    def _btn_style(self, accent=False):
        if accent:
            return """
                QPushButton {
                    background-color: #2a2a5a;
                    color: #a89cf7;
                    border: 1px solid #5a4af7;
                    border-radius: 5px;
                    font-size: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #7c6af7;
                    border-color: #a89cf7;
                    color: #fff;
                }
                QPushButton:pressed { background-color: #5a3af0; }
            """
        return """
            QPushButton {
                background-color: #1e1e3a;
                color: #7c8aaa;
                border: 1px solid #3a3a6a;
                border-radius: 5px;
                font-size: 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #2a2a5a;
                border-color: #7c6af7;
                color: #c8c8d4;
            }
            QPushButton:pressed { background-color: #3a3a7a; }
        """

    def _rgb_to_hex(self, rgb):
        try:
            r = int(max(0, min(1, rgb[0])) * 255)
            g = int(max(0, min(1, rgb[1])) * 255)
            b = int(max(0, min(1, rgb[2])) * 255)
            return f"#{r:02X}{g:02X}{b:02X}"
        except Exception:
            return "#FFFFFF"

    def _updateColorButton(self, rgb):
        try:
            r = int(max(0, min(1, rgb[0])) * 255)
            g = int(max(0, min(1, rgb[1])) * 255)
            b = int(max(0, min(1, rgb[2])) * 255)
            # Pick a readable border color (complementary brightness)
            lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
            border = "#ffffff" if lum < 0.5 else "#333333"
            self._ccButton.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({r},{g},{b});
                    border: 2px solid {border};
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    border: 2px solid #a89cf7;
                    border-radius: 5px;
                }}
            """)
        except Exception:
            pass

    # ── Public API ────────────────────────────

    def setLightColor(self, rgb):
        self._light_color = rgb
        self._updateColorButton(rgb)
        if hasattr(self, '_colorHexLabel'):
            self._colorHexLabel.setText(self._rgb_to_hex(rgb))

    def incExposure(self):
        self._exposure = min(self._exposure + self._step, self._max)
        self._refreshExposureLabel()
        self.exposure_changed.emit(self._exposure)

    def decExposure(self):
        self._exposure = max(self._exposure - self._step, -self._max)
        self._refreshExposureLabel()
        self.exposure_changed.emit(self._exposure)

    def _refreshExposureLabel(self):
        self._exposureValueLabel.setText(f"{self._exposure:+.2f}")

    def setColor(self):
        self.color_requested.emit()

    def _onPositionChanged(self, value):
        if hasattr(self, '_posValueLabel'):
            self._posValueLabel.setText(str(value))
        self.position_changed.emit(value)

    def sliderValueChanged(self, value):
        self._onPositionChanged(value)


# ─────────────────────────────────────────────
# Automatic Exposure widget  (redesigned)
# ─────────────────────────────────────────────
class CSQAEControlLayout(QWidget):

    exposure_changed = QtCore.pyqtSignal(float)

    def __init__(self, controller, uiAEonIMG=None, uiAEoffIMG=None,
                 stepE=0.2, maxE=5):
        super().__init__()
        self._controller  = controller
        self._step        = stepE
        self._max         = maxE
        self._exposureON  = 0.0
        self._exposureOFF = 0.0
        self._on_off      = True

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e3a;
                border: 1px solid #2a2a5a;
                border-radius: 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # ON/OFF toggle (text-based, clean)
        self._aeButton = QPushButton("AE  ON")
        self._aeButton.setCheckable(True)
        self._aeButton.setChecked(True)
        self._aeButton.setFixedHeight(28)
        self._aeButton.setFixedWidth(70)
        self._aeButton.setToolTip("Toggle automatic exposure")
        self._aeButton.setStyleSheet(self._toggle_style(True))

        self._deButton = QPushButton("EV −")
        self._deButton.setFixedHeight(28)
        self._deButton.setToolTip("Decrease global exposure")
        self._deButton.setStyleSheet("""
            QPushButton {
                background: #1a2a4a; color: #7cd4f7;
                border: 1px solid #2a4a6a; border-radius: 5px;
                font-weight: 600; font-size: 12px; padding: 0 10px;
            }
            QPushButton:hover { background: #2a3a6a; border-color: #7cd4f7; }
            QPushButton:pressed { background: #7cd4f7; color: #0f0f2a; }
        """)

        self._ieButton = QPushButton("EV +")
        self._ieButton.setFixedHeight(28)
        self._ieButton.setToolTip("Increase global exposure")
        self._ieButton.setStyleSheet(self._deButton.styleSheet())

        self._exposureValueLabel = QLabel("+0.00")
        self._exposureValueLabel.setFixedWidth(48)
        self._exposureValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._exposureValueLabel.setStyleSheet("""
            background-color: #0f0f22;
            color: #7cd4f7;
            border: 1px solid #2a4a6a;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 12px; font-weight: 600;
            padding: 2px 0;
        """)

        layout.addWidget(self._aeButton)
        layout.addWidget(self._deButton)
        layout.addWidget(self._ieButton)
        layout.addWidget(self._exposureValueLabel)
        layout.addStretch()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(52)

        self._aeButton.clicked.connect(self.switch_on_off)
        self._ieButton.clicked.connect(self.incExposure)
        self._deButton.clicked.connect(self.decExposure)

    def _toggle_style(self, on):
        if on:
            return """
                QPushButton { background:#1a4a2a; color:#5cf7a0;
                  border:1px solid #2a7a4a; border-radius:5px;
                  font-weight:700; font-size:11px; }
                QPushButton:hover { background:#2a6a3a; }
            """
        return """
            QPushButton { background:#3a1a1a; color:#f77c7c;
              border:1px solid #6a2a2a; border-radius:5px;
              font-weight:700; font-size:11px; }
            QPushButton:hover { background:#5a2a2a; }
        """

    def switch_on_off(self):
        self._on_off = not self._on_off
        self._aeButton.setText("AE  ON" if self._on_off else "AE OFF")
        self._aeButton.setStyleSheet(self._toggle_style(self._on_off))
        exposure = self._exposureON if self._on_off else self._exposureOFF
        self._exposureValueLabel.setText(f"{exposure:+.2f}")

    def incExposure(self):
        if self._on_off:
            self._exposureON = min(self._exposureON + self._step, self._max)
            exp = self._exposureON
        else:
            self._exposureOFF = min(self._exposureOFF + self._step, self._max)
            exp = self._exposureOFF
        self._exposureValueLabel.setText(f"{exp:+.2f}")
        self.exposure_changed.emit(exp)

    def decExposure(self):
        if self._on_off:
            self._exposureON = max(self._exposureON - self._step, -self._max)
            exp = self._exposureON
        else:
            self._exposureOFF = max(self._exposureOFF - self._step, -self._max)
            exp = self._exposureOFF
        self._exposureValueLabel.setText(f"{exp:+.2f}")
        self.exposure_changed.emit(exp)


# ─────────────────────────────────────────────
# Render display widget  (unchanged logic)
# ─────────────────────────────────────────────
class CSDisplayWidget(QWidget):

    def __init__(self, controller, title=None):
        super().__init__()
        self._controller = controller

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setScaledContents(False)
        self._label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._label.setStyleSheet("background: #0a0a18;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self._pixmap_original = None

        # Subtle inner shadow effect
        self.setStyleSheet("background: #0a0a18; border-radius: 0px;")

    def _update(self, imgDouble):
        try:
            if hasattr(imgDouble, 'dtype') and imgDouble.dtype == np.uint8:
                img = imgDouble
            else:
                img = (imgDouble * 255).astype(np.uint8)
        except Exception:
            return

        h, w, c = img.shape
        qimg = QImage(img.data, w, h, c * w, QImage.Format.Format_RGB888)
        self._pixmap_original = QPixmap.fromImage(qimg)

        target_size = self.size()
        if target_size.width() > 0 and target_size.height() > 0:
            scaled = self._pixmap_original.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._label.setPixmap(scaled)
        else:
            self._label.setPixmap(self._pixmap_original)

    def resizeEvent(self, event):
        if self._pixmap_original and not self._pixmap_original.isNull():
            scaled = self._pixmap_original.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._label.setPixmap(scaled)
        super().resizeEvent(event)

    def loadImage(self, path):
        try:
            image = QImage(path)
            if image.isNull():
                return False
            self._pixmap_original = QPixmap.fromImage(image)
            self._label.setPixmap(
                self._pixmap_original.scaled(
                    self.width(), self.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def saveImage(self, path):
        try:
            pixmap = self._label.pixmap()
            if pixmap is None or pixmap.isNull():
                return False
            return pixmap.save(path)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False


# ─────────────────────────────────────────────
# Color Wheel widget  (redesigned wrapper)
# ─────────────────────────────────────────────
class CSDisplayColorWheel(QWidget):
    """
    Roue chromatique flottante.
    - S'ouvre près du bouton couleur cliqué.
    - Se ferme si on reclique le même bouton, ou si on clique en dehors.
    - Ne bloque PAS les interactions avec le reste de l'application.
    """

    color_changed = QtCore.pyqtSignal(object)

    POPUP_SIZE = 260

    def __init__(self, controller, width=260):
        # Tool window = flottant, sans bloquer, sans barre de titre
        super().__init__(
            None,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # ne vole pas le focus
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self._controller      = controller
        self._source_btn      = None   # bouton qui a ouvert la roue
        self._app_event_filter = _WheelOutsideFilter(self)

        self._width  = self.POPUP_SIZE
        self._height = self.POPUP_SIZE
        self.setFixedSize(self._width + 20, self._height + 20)

        # Image de la roue
        colorWheelImg = (colorStudioUtils.colorWheel(self._width // 2) * 255).astype(np.uint8)
        h, w, c = colorWheelImg.shape
        qImg = QImage(colorWheelImg, w, h, c * w, QImage.Format.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qImg)

        # Container circulaire
        outer = QWidget(self)
        outer.setGeometry(10, 10, self._width, self._height)
        outer.setStyleSheet("""
            QWidget {
                background-color: #13132a;
                border: 1px solid #3a3a6a;
                border-radius: 130px;
            }
        """)

        self._label = QLabel(outer)
        self._label.setGeometry(0, 0, self._width, self._height)
        self._label.setPixmap(self._pixmap)
        self._label.setScaledContents(True)
        self._label.setStyleSheet("border-radius: 130px; background: transparent;")

        # Preview couleur au centre
        ps = 36
        self._previewLabel = QLabel(outer)
        self._previewLabel.setGeometry(
            self._width // 2 - ps // 2,
            self._height // 2 - ps // 2,
            ps, ps
        )
        self._previewLabel.setStyleSheet("""
            background-color: white;
            border: 2px solid rgba(255,255,255,0.6);
            border-radius: 18px;
        """)
        self._previewLabel.setToolTip("Couleur active")

        # Bouton fermer discret
        closeBtn = QPushButton("✕", outer)
        closeBtn.setGeometry(self._width - 28, 6, 22, 22)
        closeBtn.setStyleSheet("""
            QPushButton {
                background: rgba(30,30,60,0.8);
                color: #6666aa;
                border: 1px solid #3a3a6a;
                border-radius: 11px;
                font-size: 10px;
                font-weight: 700;
            }
            QPushButton:hover { background: #5a4af7; color: white; }
        """)
        closeBtn.clicked.connect(self.close)

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._outer = outer

    # ------------------------------------------------------------------
    # Ouvrir / fermer (toggle)
    # ------------------------------------------------------------------
    def toggleNearWidget(self, source_btn):
        """
        Si déjà visible et déclenché par le même bouton -> ferme.
        Sinon -> place et ouvre.
        """
        if self.isVisible() and self._source_btn is source_btn:
            self.close()
            return

        self._source_btn = source_btn
        self._placeNearWidget(source_btn)
        self.show()
        self.raise_()

        # Installe le filtre global pour détecter les clics en dehors
        QApplication.instance().installEventFilter(self._app_event_filter)

    def _placeNearWidget(self, source_btn):
        global_pos = source_btn.mapToGlobal(QtCore.QPoint(0, 0))
        pw, ph = self.width(), self.height()

        x = global_pos.x() - pw - 8
        y = global_pos.y() + source_btn.height() // 2 - ph // 2

        screen = QApplication.primaryScreen().availableGeometry()
        if x < screen.left():
            x = global_pos.x() + source_btn.width() + 8
        if y < screen.top():
            y = screen.top() + 4
        if y + ph > screen.bottom():
            y = screen.bottom() - ph - 4

        self.move(x, y)

    def close(self):
        QApplication.instance().removeEventFilter(self._app_event_filter)
        self._source_btn = None
        super().close()

    # ------------------------------------------------------------------
    # Sélection de couleur
    # ------------------------------------------------------------------
    def mousePressEvent(self, e):
        self._pickColor(e)

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton:
            self._pickColor(e)

    def _pickColor(self, e):
        x = int(e.position().x()) - 10
        y = int(e.position().y()) - 10

        if colorStudioUtils.inRange2D([x, y], [0, 0], [self._width, self._height]):
            w, h = self._width, self._height
            xl = 2 * (x - w / 2) / w
            yl = 2 * (y - h / 2) / h
            r  = math.sqrt(xl ** 2 + yl ** 2)

            hsv = np.zeros([1, 1, 3])
            if r < 0.5:
                hsv[0, 0] = [0.0, 0.0, 1.0]
            elif r < 1.0:
                hsv[0, 0] = [(math.atan2(xl, yl) + math.pi) / (2 * math.pi), 1.0, 1.0]
            else:
                hsv[0, 0] = [0.0, 0.0, 0.01]

            rgb = skimage.color.hsv2rgb(hsv)[0, 0]
            ri  = int(max(0, min(1, rgb[0])) * 255)
            gi  = int(max(0, min(1, rgb[1])) * 255)
            bi  = int(max(0, min(1, rgb[2])) * 255)
            self._previewLabel.setStyleSheet(f"""
                background-color: rgb({ri},{gi},{bi});
                border: 2px solid rgba(255,255,255,0.7);
                border-radius: 18px;
            """)
            self.color_changed.emit(rgb)


# ------------------------------------------------------------------
# Event filter — ferme la roue si on clique en dehors
# ------------------------------------------------------------------
class _WheelOutsideFilter(QtCore.QObject):
    def __init__(self, wheel_widget):
        super().__init__()
        self._wheel = wheel_widget

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            # Si le clic n'est pas sur la roue ni sur son bouton source
            wheel_rect  = QtCore.QRect(self._wheel.mapToGlobal(QtCore.QPoint(0, 0)),
                                       self._wheel.size())
            global_pos  = event.globalPosition().toPoint()

            inside_wheel = wheel_rect.contains(global_pos)

            inside_btn = False
            if self._wheel._source_btn is not None:
                btn = self._wheel._source_btn
                btn_rect = QtCore.QRect(btn.mapToGlobal(QtCore.QPoint(0, 0)), btn.size())
                inside_btn = btn_rect.contains(global_pos)

            if not inside_wheel and not inside_btn:
                self._wheel.close()

        return False   # ne bloque pas l'événement


# ─────────────────────────────────────────────
# Controls panel (scroll wrapper)
# ─────────────────────────────────────────────
class CSDisplayControls(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controls")
        self.setStyleSheet("background-color: #16213e;")

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ── Title bar ─────────────────────────
        titleBar = QWidget()
        titleBar.setFixedHeight(42)
        titleBar.setStyleSheet("""
            QWidget {
                background-color: #0f0f1a;
                border-bottom: 1px solid #2a2a5a;
            }
        """)
        titleLayout = QHBoxLayout(titleBar)
        titleLayout.setContentsMargins(14, 0, 14, 0)

        dot1 = QLabel("●")
        dot1.setStyleSheet("color: #f7a070; font-size: 10px; background: transparent; border:none;")
        dot2 = QLabel("●")
        dot2.setStyleSheet("color: #f7d070; font-size: 10px; background: transparent; border:none;")
        dot3 = QLabel("●")
        dot3.setStyleSheet("color: #70f7a0; font-size: 10px; background: transparent; border:none;")

        panelTitle = QLabel("LIGHTS & CONTROLS")
        panelTitle.setStyleSheet("""
            color: #5a5a8a;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
            background: transparent;
            border: none;
        """)

        titleLayout.addWidget(dot1)
        titleLayout.addWidget(dot2)
        titleLayout.addWidget(dot3)
        titleLayout.addSpacing(10)
        titleLayout.addWidget(panelTitle)
        titleLayout.addStretch()

        mainLayout.addWidget(titleBar)

        # ── Scroll area ───────────────────────
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollArea.setStyleSheet("""
            QScrollArea { border: none; background-color: #16213e; }
            QScrollBar:vertical {
                border: none; background: #1a1a2e;
                width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a6a; border-radius: 3px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #7c6af7; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        container = QWidget()
        container.setStyleSheet("background-color: #16213e;")
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(4)

        scrollArea.setWidget(container)
        mainLayout.addWidget(scrollArea)
        self.setLayout(mainLayout)


# ─────────────────────────────────────────────
# Saturation Layout  (redesigned)
# ─────────────────────────────────────────────
class CSQSaturationLayout(QVBoxLayout):

    linear_saturation_changed = QtCore.pyqtSignal(float)
    gamma_saturation_changed  = QtCore.pyqtSignal(float)

    def __init__(self, controller, range=100):
        super().__init__()
        self._controller        = controller
        self._linearSaturation  = 0.0
        self._gammaSaturation   = 0.0
        self._range             = range

        self.setSpacing(6)

        # Linear saturation
        linLbl = QLabel("Saturation")
        linLbl.setStyleSheet("color: #8888aa; font-size: 11px; font-weight: 600;")
        self._linearSaturationValueLabel = QLabel("+0")
        self._linearSaturationValueLabel.setFixedWidth(32)
        self._linearSaturationValueLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._linearSaturationValueLabel.setStyleSheet(
            "color: #a89cf7; font-family: 'Consolas', monospace; font-size: 11px;"
        )
        self._resetLinearButton = QPushButton("↺")
        self._resetLinearButton.setFixedSize(22, 22)
        self._resetLinearButton.setToolTip("Reset linear saturation")
        self._resetLinearButton.setStyleSheet("""
            QPushButton { background:#1e1e3a; color:#6666aa;
              border:1px solid #3a3a6a; border-radius:4px; font-size:13px; }
            QPushButton:hover { color:#a89cf7; border-color:#7c6af7; }
        """)

        linRow = QHBoxLayout()
        linRow.addWidget(linLbl)
        linRow.addStretch()
        linRow.addWidget(self._linearSaturationValueLabel)
        linRow.addWidget(self._resetLinearButton)
        self.addLayout(linRow)

        self._sliderLinearSaturation = QSlider(Qt.Orientation.Horizontal)
        self._sliderLinearSaturation.setValue(50)
        self._sliderLinearSaturation.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addWidget(self._sliderLinearSaturation)

        # Gamma saturation
        gamLbl = QLabel("Gamma Sat.")
        gamLbl.setStyleSheet("color: #8888aa; font-size: 11px; font-weight: 600;")
        self._gammaSaturationValueLabel = QLabel("+0")
        self._gammaSaturationValueLabel.setFixedWidth(32)
        self._gammaSaturationValueLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._gammaSaturationValueLabel.setStyleSheet(
            "color: #7cd4f7; font-family: 'Consolas', monospace; font-size: 11px;"
        )
        self._resetGammaButton = QPushButton("↺")
        self._resetGammaButton.setFixedSize(22, 22)
        self._resetGammaButton.setToolTip("Reset gamma saturation")
        self._resetGammaButton.setStyleSheet(self._resetLinearButton.styleSheet())

        gamRow = QHBoxLayout()
        gamRow.addWidget(gamLbl)
        gamRow.addStretch()
        gamRow.addWidget(self._gammaSaturationValueLabel)
        gamRow.addWidget(self._resetGammaButton)
        self.addLayout(gamRow)

        self._sliderGammaSaturation = QSlider(Qt.Orientation.Horizontal)
        self._sliderGammaSaturation.setValue(50)
        self._sliderGammaSaturation.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addWidget(self._sliderGammaSaturation)

        # Signals
        self._sliderLinearSaturation.valueChanged.connect(self.sliderLinearSaturationValueChanged)
        self._sliderGammaSaturation.valueChanged.connect(self.sliderGammaSaturationValueChanged)
        self._resetLinearButton.clicked.connect(self.resetLinear)
        self._resetGammaButton.clicked.connect(self.resetGamma)

    def sliderLinearSaturationValueChanged(self, value):
        self._linearSaturation = (2 * value / 100.0 - 1.0) * self._range
        self._linearSaturationValueLabel.setText(f"{self._linearSaturation:+.0f}")
        self.linear_saturation_changed.emit(self._linearSaturation)

    def sliderGammaSaturationValueChanged(self, value):
        self._gammaSaturation = (2 * value / 100.0 - 1.0) * self._range
        self._gammaSaturationValueLabel.setText(f"{self._gammaSaturation:+.0f}")
        self.gamma_saturation_changed.emit(self._gammaSaturation)

    def resetLinear(self):
        self._sliderLinearSaturation.setValue(50)

    def resetGamma(self):
        self._sliderGammaSaturation.setValue(50)


# ─────────────────────────────────────────────
# Legacy stubs (kept for backward compat)
# ─────────────────────────────────────────────
class CSQIMGButton(QPushButton):
    def __init__(self, qicon, size, name="noname"):
        super().__init__()
        self.setIcon(qicon)
        self.name = name
        x, y = size
        self.setIconSize(QtCore.QSize(x, y))
        self.clicked.connect(self.cbClicked)

    def cbClicked(self): pass


class CSQIMGSwitchButton(QPushButton):
    def __init__(self, qiconOn, qiconOff, size, name="noname"):
        super().__init__()
        self.iconOn = qiconOn
        self.iconOff = qiconOff
        self.on = True
        self.setIcon(self.iconOn)
        self.name = name
        x, y = size
        self.setIconSize(QtCore.QSize(x, y))
        self.clicked.connect(self.cbClicked)

    def cbClicked(self):
        self.on = not self.on
        self.setIcon(self.iconOn if self.on else self.iconOff)


class CSQLoadSaveLayout(QHBoxLayout):
    def __init__(self, qiconLoad, qiconSave):
        super().__init__()
        self.loadButton = CSQIMGButton(qiconLoad, (50, 50), name="load button")
        self.saveButton = CSQIMGButton(qiconSave, (50, 50), name="save button")
        self.addWidget(self.loadButton)
        self.addWidget(self.saveButton)