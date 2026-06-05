# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""
import sys

from PyQt6.QtWidgets import QApplication

import models.colorStudioModel as colorStudioModel
import views.colorStudioWidget as colorStudioWidget
import controllers.colorStudioController as colorStudioController
import utils.colorStudioUtils as colorStudioUtils
import views.colorStudioUIBuilder as colorStudioUIBuilder

# ----------------------------------------------------------------------------------		
print("ColorStudio - Charlotte Germe Luc Telliez Chloé Faillie - 2026")
print("-------------------------------")
screenX, screenY = colorStudioWidget.getScreenSize()
print("screen resolution: ",screenX,"x",screenY)
colorStudioUIBuilder.CSUIBuilder.setTemplate(screenX,screenY)

# Qt init
app = QApplication.instance() 
if not app:
    app = QApplication(sys.argv)

# build GUI (sans scène initiale)
ui = colorStudioUIBuilder.CSUIAllBuilder()

# run app for event management
app.exec()