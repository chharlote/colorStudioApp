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

from PyQt6.QtWidgets import QApplication, QFileDialog

import models.colorStudioModel as colorStudioModel
import views.colorStudioWidget as colorStudioWidget
import controllers.colorStudioController as colorStudioController
import utils.colorStudioUtils as colorStudioUtils
import views.colorStudioUIBuilder as colorStudioUIBuilder

# ----------------------------------------------------------------------------------		
print("ColorStudio - Rémi Cozot - 2019")
print("-------------------------------")
screenX, screenY = colorStudioWidget.getScreenSize()
print("screen resolution: ",screenX,"x",screenY)
colorStudioUIBuilder.CSUIAllBuilder.setTemplate(screenX,screenY)

# Qt init
app = QApplication.instance() 
if not app:  app = QApplication(sys.argv)

# select input file name
defaultFilename = "./fichier_json_test1.json" 
inputFilename, _ = QFileDialog.getOpenFileName(
    None,                                   
    "Color Studio - Select light-setup file", 
    "",                                     
    "JSON files (*.json);;All files (*.*)"   
)
print("ColorStudio: inuput file>",inputFilename)

if not inputFilename: 
    inputFilename = defaultFilename
    print("ColorStudio: action annulée, utilisation du fichier par défaut >", inputFilename)
else:
    print("ColorStudio: input file >", inputFilename)


# scene object
lightsScene = colorStudioModel.Scene()
# load scene from json
lightsScene.fromJSON(inputFilename,colorStudioUIBuilder.CSUIBuilder.template['scale'])
# print scene
lightsScene.print()

# build GUI according to scene
ui = colorStudioUIBuilder.CSUIAllBuilder(lightsScene)

# run app for event management
app.exec()

