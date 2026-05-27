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

import math
import numpy as np
import skimage

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QToolButton, QSizePolicy, QScrollArea
from PyQt6.QtGui import QIcon, QPixmap, QImage, QSurfaceFormat
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import models.colorStudioModel as colorStudioModel
import utils.colorStudioUtils as colorStudioUtils
import views.colorStudioUIBuilder as colorStudioUIBuilder

# functions
# ----------------------------------------------------------------------------------
def getScreenSize():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()

    x = size.width()
    y = size.height()

    app.quit()

    return (x,y)

# ----------------------------------------------------------------------------------
# classes
# ----------------------------------------------------------------------------------
class QModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super(QModernGLWidget, self).__init__()
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setSamples(4)
        self.timer = QtCore.QElapsedTimer()

    def initializeGL(self):
        pass

    def paintGL(self):
        self.ctx = moderngl.create_context()
        self.screen = self.ctx.detect_framebuffer()
        self.init()
        self.render()
        self.paintGL = self.render

    def init(self):
        pass

    def render(self):
        pass
# ----------------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------------
class PanTool:
    def __init__(self):
        self.total_x = 0.0
        self.total_y = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.delta_x = 0.0
        self.delta_y = 0.0
        self.drag = False

    def start_drag(self, x, y):
        self.start_x = x
        self.start_y = y
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
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)
# ----------------------------------------------------------------------------------
pan_tool = PanTool()
# ----------------------------------------------------------------------------------
class MyWidgetGL(QModernGLWidget):
    def __init__(self, img, scene=None):
        super(MyWidgetGL, self).__init__()
        self.VBOdata = colorStudioUtils.img2chromaVertices(img, False)
        self.setWindowTitle("3D Color")


    def init(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.scene = HelloWorld2D(self.ctx)

    def resizeGL(self, width, height):
        if hasattr(self, 'ctx'):
            self.ctx.viewport = (0, 0, width, height)

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

    def _update(self,img):
        self.VBOdata = colorStudioUtils.img2chromaVertices(img, False)
        self.update()

    def loadImage(self, path):
        image = QImage(path)
        if image.isNull():
            return False
        pixmap = QPixmap.fromImage(image)
        self._label.setPixmap(pixmap)
        return True

    def saveImage(self, path):
        pixmap = self._label.pixmap()
        if pixmap is None:
            return False
        return pixmap.save(path)
# ----------------------------------------------------------------------------------
class CSQIMGButton(QPushButton):

	def __init__(self,qicon,size,name="noname"):
		# qicon 	(QIcon)
		# size 		((x,y))
		# name 		(String)
		super().__init__()
		self.setIcon(qicon)
		self.name = name
		x,y = size
		self.setIconSize(QtCore.QSize(x,y))
		self.clicked.connect(self.cbClicked)
		
	def cbClicked(self): pass
# ----------------------------------------------------------------------------------
class CSQIMGSwitchButton(QPushButton):

	def __init__(self,qiconOn,qiconOff,size,name="noname"):
		# qicon 	(QIcon)
		# size 		((x,y))
		# name 		(String)
		super().__init__()
		self.iconOn = qiconOn
		self.iconOff = qiconOff
		# default state : on (true)
		self.on = True
		self.setIcon(self.iconOn)
		self.name = name
		x,y = size
		self.setIconSize(QtCore.QSize(x,y))
		self.clicked.connect(self.cbClicked)
		
	def cbClicked(self):
		self.on = not(self.on)
		if self.on:
			self.setIcon(self.iconOn)
		else:
			self.setIcon(self.iconOff)

# ----------------------------------------------------------------------------------
class CSQLoadSaveLayout(QHBoxLayout):

	def __init__(self,qiconLoad,qiconSave):
		super().__init__()
		
		# create load and save button
		self.loadButton = CSQIMGButton(qiconLoad,(50,50),name="load button")
		self.saveButton = CSQIMGButton(qiconSave,(50,50),name="save button")
	
		# add button to layout
		self.addWidget(self.loadButton)
		self.addWidget(self.saveButton)
# ----------------------------------------------------------------------------------
class CSQLightControlLayout(QVBoxLayout):

    exposure_changed = pyqtSignal(float)
    color_requested = pyqtSignal()
    position_changed = pyqtSignal(int)
    
    def __init__(self,controller,uiDEIMG=None,uiIEIMG=None,uiCCIMG=None,stepE=0.2,maxE=5,lightPosIdx=50, light_name=None, light_color=None):
        """
        widget that controls exposure, color and position of light
        @params:
            controller  - Required   (CSLightController)
            uiDEIMG     - Optional  : icon for Decrease Exposure (Qicon)
            uiIEIMG     - Optional  : icon for Increase Exposure (Qicon)
            uiCCIMG     - Optional  : icon for color control     (Qicon)
            stepE       - Optional  : exposure step [=0.2]       (Float)
            maxE        - Optional  : max exposure  [=5.O]       (Float)
            light_color - Optional  : RGB color tuple [0,1]      (tuple)
       """
        super().__init__()
        # controller 
        self._controller = controller

        # manage default Qicon
        if uiDEIMG == None : uiDEIMG = colorStudioUIBuilder.CSUIBuilder.uiDEIMG 
        if uiIEIMG == None : uiIEIMG = colorStudioUIBuilder.CSUIBuilder.uiIEIMG
        if uiCCIMG == None : uiCCIMG = colorStudioUIBuilder.CSUIBuilder.uiCCIMG

        # visible name label so user sees which light is controlled
        name = light_name if light_name is not None else "Light"
        self._nameLabel = QLabel(f"<b>{name}</b>")
        self._nameLabel.setFixedHeight(25)
        
        # control of Exposure
        self._step 	= stepE
        self._max 	= maxE
        self._exposure = 0.0
        self._light_color = light_color if light_color is not None else (1.0, 1.0, 1.0)
        
        # Row 1: Light name
        self.addWidget(self._nameLabel)
        
        # Row 2: Exposure controls (-, value, +)
        exposureLayout = QHBoxLayout()
        
        exposureLabel = QLabel("Exposure")
        exposureLabel.setFixedWidth(60)
        
        self._deButton = QPushButton("-")
        self._deButton.setFixedWidth(40)
        self._deButton.setToolTip(f"{name}: Decrease exposure")
        self._deButton.setAccessibleName(f"{name} decrease exposure")
        
        self._exposureValueLabel = QLabel("+0.00")
        self._exposureValueLabel.setFixedWidth(60)
        self._exposureValueLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._exposureValueLabel.setToolTip(f"{name}: exposure value")
        
        self._ieButton = QPushButton("+")
        self._ieButton.setFixedWidth(40)
        self._ieButton.setToolTip(f"{name}: Increase exposure")
        self._ieButton.setAccessibleName(f"{name} increase exposure")
        
        exposureLayout.addWidget(exposureLabel)
        exposureLayout.addWidget(self._deButton)
        exposureLayout.addWidget(self._exposureValueLabel)
        exposureLayout.addWidget(self._ieButton)
        exposureLayout.addStretch()
        self.addLayout(exposureLayout)
        
        # Row 3: Color control
        colorLayout = QHBoxLayout()
        self._ccButton = QPushButton()
        self._ccButton.setFixedSize(50, 50)
        self._ccButton.setToolTip(f"{name}: Change color")
        self._ccButton.setAccessibleName(f"{name} change color")
        # Set initial color on button
        self._updateColorButton(self._light_color)
        
        colorLabel = QLabel("Color")
        colorLabel.setFixedWidth(50)
        colorLayout.addWidget(colorLabel)
        colorLayout.addWidget(self._ccButton)
        colorLayout.addStretch()
        self.addLayout(colorLayout)
        
        # Row 4: Position slider with label
        positionLayout = QHBoxLayout()
        positionLabel = QLabel("Position")
        positionLabel.setFixedWidth(60)
        self._sliderPosition = QSlider(QtCore.Qt.Orientation.Horizontal)
        self._sliderPosition.setValue(lightPosIdx)
        self._sliderPosition.setToolTip(f"{name}: Light position")
        positionLayout.addWidget(positionLabel)
        positionLayout.addWidget(self._sliderPosition)
        self.addLayout(positionLayout)

        # set onClick callback
        self._ieButton.clicked.connect(self.incExposure)
        self._deButton.clicked.connect(self.decExposure)
        self._ccButton.clicked.connect(self.setColor)

        # slider
        self._sliderPosition.valueChanged.connect(self.sliderValueChanged)
        
        # Add stretch at end to prevent excessive vertical spacing
        self.addStretch()

    def _updateColorButton(self, rgb):
        """Update the color button background with the light color"""
        try:
            # Ensure rgb values are in [0,1] range
            r = max(0, min(1, rgb[0]))
            g = max(0, min(1, rgb[1]))
            b = max(0, min(1, rgb[2]))
            
            # Convert to 0-255 range for QColor
            r_int = int(r * 255)
            g_int = int(g * 255)
            b_int = int(b * 255)
            
            # Set button background color
            self._ccButton.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({r_int}, {g_int}, {b_int});
                    border: 2px solid #333;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid #666;
                }}
            """)
        except Exception:
            pass

    def setLightColor(self, rgb):
        """Update the light color and display it on the button"""
        self._light_color = rgb
        self._updateColorButton(rgb)

    def incExposure(self):
        self._exposure = self._exposure + self._step
        if self._exposure > self._max: self._exposure = self._max
        expoString = "{:+.2f}".format(self._exposure)
        self._exposureValueLabel.setText(expoString)
        self.exposure_changed.emit(self._exposure)
        
    def decExposure(self):
        self._exposure = self._exposure - self._step
        if self._exposure < -self._max: self._exposure = -self._max
        expoString = "{:+.2f}".format(self._exposure)
        self._exposureValueLabel.setText(expoString)
        self.exposure_changed.emit(self._exposure)

    def setColor(self): self.color_requested.emit()
    
    def sliderValueChanged(self,value): self.position_changed.emit(value)
# ----------------------------------------------------------------------------------
class CSQCollapsibleSection(QWidget):

    def __init__(self, title, expanded=False, parent=None):
        super().__init__(parent)

        self._toggleButton = QToolButton()
        self._toggleButton.setText(title)
        self._toggleButton.setCheckable(True)
        self._toggleButton.setChecked(expanded)
        self._toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggleButton.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        self._toggleButton.clicked.connect(self._on_toggle)

        self._content = QWidget()
        self._contentLayout = QVBoxLayout(self._content)
        self._contentLayout.setContentsMargins(15, 0, 0, 0)
        self._contentLayout.setSpacing(6)
        self._content.setVisible(expanded)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.addWidget(self._toggleButton)
        self._layout.addWidget(self._content)

    def _on_toggle(self):
        expanded = self._toggleButton.isChecked()
        self._toggleButton.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        self._content.setVisible(expanded)

    def addWidget(self, widget):
        self._contentLayout.addWidget(widget)

    def addLayout(self, layout):
        self._contentLayout.addLayout(layout)

# ----------------------------------------------------------------------------------
class CSQAEControlLayout(QWidget):

    exposure_changed = QtCore.pyqtSignal(float)
    
    def __init__(self, controller, uiAEonIMG=None,uiAEoffIMG=None,stepE=0.2,maxE=5):

        super().__init__()

        # controller
        self._controller = controller

        # control of Exposure
        self._Ytarget = 0.5
        self._step 	= stepE
        self._max 	= maxE
        self._exposureON = 0.0
        self._exposureOFF = 0.0
        self._on_off = True

        # manage default Qicon
        if uiAEonIMG == None : uiAEonIMG = colorStudioUIBuilder.CSUIBuilder.uiAEonIMG 
        if uiAEoffIMG == None : uiAEoffIMG = colorStudioUIBuilder.CSUIBuilder.uiAEoffIMG

        # create layout and widgets
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self._aeButton = CSQIMGSwitchButton(uiAEonIMG, uiAEoffIMG, (40,40), name="switch AE")
        self._ieButton = QPushButton("EV +")
        self._deButton = QPushButton("EV -")
        self._exposureValueLabel = QLabel("+0.00")
        self._exposureValueLabel.setFixedWidth(50)
        self._exposureValueLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._aeLabel = QLabel("Auto Exposure")
        self._aeLabel.setFixedWidth(100)

        self._aeButton.setToolTip("Enable/disable automatic exposure")
        self._ieButton.setToolTip("Increase exposure")
        self._deButton.setToolTip("Decrease exposure")

        layout.addWidget(self._aeLabel)
        layout.addWidget(self._aeButton)
        layout.addWidget(self._deButton)
        layout.addWidget(self._ieButton)
        layout.addWidget(self._exposureValueLabel)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(60)
        self.setStyleSheet("QWidget { background: rgba(255,255,255,0.9); border: 1px solid #aaa; border-radius: 4px; }")

        # set onClick callback
        self._aeButton.clicked.connect(self.switch_on_off)
        self._ieButton.clicked.connect(self.incExposure)
        self._deButton.clicked.connect(self.decExposure)

    def switch_on_off(self):
        self._on_off = not(self._on_off)
        if self._on_off : exposure = self._exposureON
        else : exposure = self._exposureOFF
        expoString = "{:+.2f}".format(exposure)
        self._exposureValueLabel.setText(expoString)

    def incExposure(self):
        if self._on_off:
            self._exposureON = min(self._exposureON + self._step, self._max)
            exposure = self._exposureON
        else:
            self._exposureOFF = min(self._exposureOFF + self._step, self._max)
            exposure = self._exposureOFF
        expoString = "{:+.2f}".format(exposure)
        self._exposureValueLabel.setText(expoString)
        self.exposure_changed.emit(exposure)

    def decExposure(self):
        if self._on_off:
            self._exposureON = max(self._exposureON - self._step, -self._max)
            exposure = self._exposureON
        else:
            self._exposureOFF = max(self._exposureOFF - self._step, -self._max)
            exposure = self._exposureOFF
        expoString = "{:+.2f}".format(exposure)
        self._exposureValueLabel.setText(expoString)
        self.exposure_changed.emit(exposure)
# ----------------------------------------------------------------------------------		
class CSDisplayWidget(QWidget):

    def __init__(self, controller, title=None):
        super().__init__()

        self._controller = controller

        self._label = QLabel(self)
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # IMPORTANT: casse boucle layout
        self._label.setScaledContents(False)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self._pixmap_original = None

    # ----------------------------------------------------

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

        # Scale the displayed pixmap to the current widget size so color updates
        # do not force the widget to grow to the raw image resolution.
        target_size = self.size()
        if target_size.width() > 0 and target_size.height() > 0:
            scaled = self._pixmap_original.scaled(
                target_size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            self._label.setPixmap(scaled)
        else:
            self._label.setPixmap(self._pixmap_original)

    # ----------------------------------------------------

    def resizeEvent(self, event):

        if self._pixmap_original and not self._pixmap_original.isNull():

            scaled = self._pixmap_original.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )

            self._label.setPixmap(scaled)

        super().resizeEvent(event)

    def loadImage(self, path):
        """Load an image from file and display it in the render widget"""
        try:
            image = QImage(path)
            if image.isNull():
                print(f"Error: Cannot load image from {path}")
                return False
            pixmap = QPixmap.fromImage(image)
            self._pixmap_original = pixmap
            target_w = max(1, self.width())
            target_h = max(1, self.height())
            scaled = self._pixmap_original.scaled(target_w, target_h, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self._label.setPixmap(scaled)
            print(f"Image loaded from {path}")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def saveImage(self, path):
        """Save the current displayed image to file"""
        try:
            pixmap = self._label.pixmap()
            if pixmap is None or pixmap.isNull():
                print("Error: No image to save")
                return False
            success = pixmap.save(path)
            if success:
                print(f"Image saved to {path}")
            else:
                print(f"Error: Failed to save image to {path}")
            return success
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

# ----------------------------------------------------------------------------------
class CSDisplayColorWheel(QWidget):

    color_changed = QtCore.pyqtSignal(object)
    
    def __init__(self,controller, width=480):
        super().__init__()
        # controller 
        self._controller = controller

        # size
        if isinstance(width, (tuple, list)) and len(width) == 2:
            self._width, self._height = int(width[0]), int(width[1])
        else:
            self._width = int(width)
            self._height = int(width)

        # title and window size
        self.setWindowTitle("Color Wheel:: __ no active light __")
        self.setFixedSize(self._width, self._height)

        # image (color wheel)
        colorWheelImg = (colorStudioUtils.colorWheel(self._width//2)*255).astype(np.uint8)
        height, width, channel = colorWheelImg.shape
        bytesPerLine = channel * width
        qImg = QImage(colorWheelImg, width, height, bytesPerLine, QImage.Format.Format_RGB888)

        # store pixmap in object
        self._pixmap = QPixmap.fromImage(qImg)
        self._label = QLabel(self)
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._label.setPixmap(self._pixmap)
        self._label.setScaledContents(True)

        # layout so the label fills the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        # mouse
        self.setMouseTracking(True)  

    def mousePressEvent(self,e): self.mouseMoveEvent(e)

    def mouseMoveEvent(self, e):
        # mouse position
        x, y = int(e.position().x()), int(e.position().y())

        # hsv color
        hsv_array = np.zeros([1,1,3])

        if colorStudioUtils.inRange2D([x,y],[0,0], [self._width,self._height]):
            # compute local coordinate
            w,h = self._width,  self._height
            x_local = 2*(x-w/2)/w
            y_local = 2*(y-h/2)/h
            r = math.sqrt(x_local*x_local+y_local*y_local)
                        
            if r<0.5: hsv_array[0,0,:] = [0.0,0.0,1.0]
            elif r<1.0:	hsv_array[0,0,:] = [(math.atan2(x_local,y_local)+math.pi)/(2*math.pi),1.0,1.0]
            else: hsv_array[0,0,:] = [0.0,0.0,0.01]

            rgb_hsv_array = skimage.color.hsv2rgb(hsv_array)   
            rgb = rgb_hsv_array[0,0]

            # controller
            self.color_changed.emit(rgb)
# ----------------------------------------------------------------------------------		
class CSDisplayControls(QWidget):
    def __init__(self):
        super().__init__()

        # window title
        self.setWindowTitle("Control Window")
        
        # Main layout for the widget
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        
        # Create scroll area for handling multiple expanded light sections
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                border: 1px solid #ddd;
                background-color: #f5f5f5;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #bbb;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #999;
            }
        """)
        
        # Container widget inside scroll area
        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(10)
        
        scrollArea.setWidget(container)
        mainLayout.addWidget(scrollArea)
        self.setLayout(mainLayout)
# ----------------------------------------------------------------------------------		
class CSQSaturationLayout(QVBoxLayout):
    
    linear_saturation_changed = QtCore.pyqtSignal(float)
    gamma_saturation_changed = QtCore.pyqtSignal(float)

    def __init__(self,controller,range=100):
        """
        widget that controls exposure, color and position of light
        @params:
            controller  - Required                                  (CSSaturationController)
            range       - Optional  :  range [-range,range]         (Float)
       """
        super().__init__()
        # controller 
        self._controller = controller

        # control of saturation
        self._linearSaturation 	= 0.0
        self._gammaSaturation 	= 0.0
        self._range 	        = range

        # create 
        self._linearSaturationValueLabel = QLabel("linear saturation: "+"{:+.0f}".format(self._linearSaturation))
        self._sliderLinearSaturation = QSlider(QtCore.Qt.Orientation.Horizontal)
        self._sliderLinearSaturation.setValue(50)

        self._gammaSaturationValueLabel = QLabel("gamma saturation: "+"{:+.0f}".format(self._gammaSaturation))
        self._sliderGammaSaturation = QSlider(QtCore.Qt.Orientation.Horizontal)
        self._sliderGammaSaturation.setValue(50)

        # reset buttons (linear and gamma)
        self._resetLinearButton = QPushButton("Reset")
        self._resetGammaButton = QPushButton("Reset")

        # add  to layout with reset buttons
        linearRow = QHBoxLayout()
        linearRow.addWidget(self._linearSaturationValueLabel)
        linearRow.addStretch()
        linearRow.addWidget(self._resetLinearButton)

        gammaRow = QHBoxLayout()
        gammaRow.addWidget(self._gammaSaturationValueLabel)
        gammaRow.addStretch()
        gammaRow.addWidget(self._resetGammaButton)

        self.addLayout(linearRow)
        self.addWidget(self._sliderLinearSaturation)
        self.addLayout(gammaRow)
        self.addWidget(self._sliderGammaSaturation)

        # slider
        self._sliderLinearSaturation.valueChanged.connect(self.sliderLinearSaturationValueChanged) 
        self._sliderGammaSaturation.valueChanged.connect(self.sliderGammaSaturationValueChanged) 

        # reset callbacks
        self._resetLinearButton.clicked.connect(self.resetLinear)
        self._resetGammaButton.clicked.connect(self.resetGamma)

    def sliderLinearSaturationValueChanged(self,value): 
        self._linearSaturation = (2*value/100.0 -1.0)*self._range
        self._linearSaturationValueLabel.setText("saturation: "+"{:+.0f}".format(self._linearSaturation))
        self.linear_saturation_changed.emit(self._linearSaturation)

    def sliderGammaSaturationValueChanged(self,value): 
        self._gammaSaturation = (2*value/100.0 -1.0)*self._range
        self._gammaSaturationValueLabel.setText("gamma saturation: "+"{:+.0f}".format(self._gammaSaturation))
        self.gamma_saturation_changed.emit(self._gammaSaturation)

    def resetLinear(self):
        # set slider to midpoint (50)
        self._sliderLinearSaturation.setValue(50)
        self.sliderLinearSaturationValueChanged(50)

    def resetGamma(self):
        self._sliderGammaSaturation.setValue(50)
        self.sliderGammaSaturationValueChanged(50)
# ----------------------------------------------------------------------------------
