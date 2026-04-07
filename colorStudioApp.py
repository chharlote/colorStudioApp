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

import easygui

from PyQt5.QtWidgets import QApplication

import colorStudioModel
import colorStudioWidget
import colorStudioController
import colorStudioUtils
import colorStudioUIBuilder

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
defaultFilename = "./xml-2019-6-7-22-47-1.xml" 
inputFilename =  easygui.fileopenbox(msg="select light-settup file",title="Color Studio",default='xml*.xml',filetypes=["*.xml","xml files"],multiple=False)
print("ColorStudio: inuput file>",inputFilename)

if inputFilename == None: 
    inputFilename= defaultFilename
    print("ColorStudio: inuput file>",inputFilename)


# scene object
lightsScene = colorStudioModel.Scene()
# load scene from xml
lightsScene.fromXML(inputFilename,colorStudioUIBuilder.CSUIBuilder.template['scale'])
# print scene
lightsScene.print()

# build GUI according to scene
ui = colorStudioUIBuilder.CSUIAllBuilder(lightsScene)

# run app for event management
app.exec_()

