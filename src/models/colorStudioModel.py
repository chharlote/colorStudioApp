# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""

from utils.colorStudioUtils import loadImage, printProgressBar, image2Ymean

import math
import numpy as np
import skimage
import json
import cv2

# ----------------------------------------------------------------------------------
#  IMAGES
# ----------------------------------------------------------------------------------
class Images:
    """
    set of images (supports both LDR and HDR formats)
    """
    def __init__(self,pathImage,baseImageName,extImageName,nbImage,nbDigit,load=True, scale=0.5, isHDR=False, target_shape=None, progress_callback=None, light_name=""):
        self._pathImage = pathImage
        self._baseImageName = baseImageName
        self._extImageName = extImageName
        self._nbImage = nbImage
        self._nbDigit = nbDigit
        self._isHDR = isHDR
        self._images = []
        
        self._progress_cb = progress_callback
        self._light_name = light_name

        if load:  self.loadImages(scale, target_shape)

    def loadImages(self, scale=0.5, target_shape=None):
        progress_total = max(1, self._nbImage - 1)

        for i in range(self._nbImage):
            printProgressBar(i, progress_total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█')
            
            if self._progress_cb is not None:
                try:
                    self._progress_cb(i, self._nbImage, self._light_name)
                except Exception:
                    pass

            iStr = str(i).zfill(self._nbDigit)
            name = self._pathImage+self._baseImageName+iStr+self._extImageName

            img = loadImage(name, scale)

            if target_shape is not None and img.shape != target_shape:
                img = skimage.transform.resize(
                    img,
                    target_shape,
                    preserve_range=True,
                    anti_aliasing=True,
                )
            self._images.append(img)

    def clear(self): self._images.clear()
    def len(self): return self._nbImage
    def isHDR(self): return self._isHDR

# ----------------------------------------------------------------------------------
#  LIGHT
# ----------------------------------------------------------------------------------
class Light:
	lightNb = 0
	
	def __init__(self,name=None):
		if not name:	
			self._name = "Light"+str(Light.lightNb)
		else:
			self._name = name
	
		Light.lightNb = Light.lightNb+1
		self._npColorRGB = np.asarray([1.0,1.0,1.0])
		self._exposure = 0
		self._imageIdx = 0
		self._maxIdx = 0
		self._ImagesArray = None
		self._needUpdate = False
		self._firstUpdate = True
		self._currentImage = None

	def setImagesArray(self, imgArray):
		self._ImagesArray = imgArray
		self._maxIdx = self._ImagesArray.len()
	
	def clear(self): self._ImagesArray.clear()
		
	def setExposure(self,expValue):
		self._exposure = expValue
		self._needUpdate = True

	def setColor(self,color):
		self._npColorRGB = color
		self._needUpdate = True
	
	def setImageIdx(self,idx):
		if self._ImagesArray and self._ImagesArray._images:
			max_idx = len(self._ImagesArray._images) - 1
			idx = min(max(idx, 0), max_idx)
		self._imageIdx = idx
		self._needUpdate = True
	
	def render(self):
		if self._firstUpdate or self._needUpdate:
			img = self._ImagesArray._images[self._imageIdx]
			imgOut = img * self._npColorRGB * math.pow(2, self._exposure)
			self._currentImage = imgOut
			self._firstUpdate = False
			self._needUpdate = False
		else:
			imgOut = self._currentImage
		return imgOut
	
	def print(self):
		print("[ Light:",self._name, ",", "imgIdx:",self._imageIdx,"/",self._maxIdx,",", "exposure:",self._exposure, "color:","[ r:",self._npColorRGB[0],", g:",self._npColorRGB[1],",b:",self._npColorRGB[2],"]", "]")

# ----------------------------------------------------------------------------------
#  SCENE
# ----------------------------------------------------------------------------------
class Scene:
    def __init__(self, hdr = False):
        self._lights = []           
        self._postProcesses = []    
        self._hdr = hdr

    def addLight(self,light): self._lights.append(light)
    def addPostProcess(self, postProcess): self._postProcesses.append(postProcess)

    def clear(self):
        self._lights.clear()
        self._postProcesses.clear()

    def getLightByName(self,name):
        returnLight = None
        for light in self._lights :
            if light._name == name :
                returnLight = light
                break
        return returnLight

    def render(self):
        imgOut = np.zeros(self._lights[0]._ImagesArray._images[0].shape)
        for light in self._lights:
            lightImg = light.render()
            imgOut = imgOut + lightImg
        for pp in self._postProcesses:
            imgOut = pp.postProcess(imgOut)
        if not self._hdr :
            imgOut = np.clip(imgOut,0.0,1.0)
        return imgOut

    def fromJSON(self, jsonFile, scale=0.5, progress_callback=None):
        self._lights.clear()

        with open(jsonFile, 'r', encoding='utf-8') as f:
            data = json.load(f)

        lights_data = data.get('lights', [])
        filenameLight = {}

        for light_data in lights_data:
            lightName = light_data.get('name', 'Light')

            input_data = light_data.get('inputFile', {})
            ext = input_data.get('ext', '.jpg')
            max_value = int(input_data.get('max', 100))
            digit = int(input_data.get('digit', 4))
            imagesFile = input_data.get('path', '')
            isHDR = input_data.get('isHDR', False)

            idxPos = int(light_data.get('idxPos', 0))
            exp = float(light_data.get('exp', 0.0))

            color_data = light_data.get('color', {})
            rr = float(color_data.get('r', 1.0))
            gg = float(color_data.get('g', 1.0))
            bb = float(color_data.get('b', 1.0))

            light = Light(name=lightName)
            light.setExposure(exp)
            light.setColor(np.asarray([rr, gg, bb]))
            light.setImageIdx(idxPos)
            images = Images('', imagesFile, ext, max_value, digit, load=False, isHDR=isHDR)
            light.setImagesArray(images)

            self._lights.append(light)

            if imagesFile in filenameLight:
                filenameLight[imagesFile].append(light)
            else:
                filenameLight.update({imagesFile: [light]})

        target_shape = None 
        
        for k in filenameLight.keys():
            lights = filenameLight[k]
            firstLight = lights[0]
            
            imgs = Images(
                firstLight._ImagesArray._pathImage,
                firstLight._ImagesArray._baseImageName,
                firstLight._ImagesArray._extImageName,
                firstLight._ImagesArray._nbImage,
                firstLight._ImagesArray._nbDigit,
                load=True, 
                scale=scale, 
                isHDR=firstLight._ImagesArray.isHDR(),
                target_shape=target_shape,
                progress_callback=progress_callback,
                light_name=firstLight._name) 

            if target_shape is None and len(imgs._images) > 0:
                target_shape = imgs._images[0].shape

            for li in lights:
                li.setImagesArray(imgs)

    def print(self):
        print(" -------- LIGHTS -------- ")
        for l in self._lights: l.print()

# ----------------------------------------------------------------------------------
#  POST PROCESS
# ----------------------------------------------------------------------------------
class PostProcess:
	def __init__(self): pass
	def postProcess(self,img): return img

class Saturation(PostProcess):
    def __init__(self,linearSat=0,gammaSat=0):
        self._linearSaturation = linearSat
        self._gammaSaturation = gammaSat
        self._saturationRange = 1.0

    def setLinearSaturation(self,saturation): self._linearSaturation = saturation
    def setGammaSaturation(self,vibrance): self._gammaSaturation = vibrance

    def postProcess(self, img):
            if self._linearSaturation == 0 and self._gammaSaturation == 0:
                return img

            img_f32 = img.astype(np.float32)
            imgHSV = cv2.cvtColor(img_f32, cv2.COLOR_RGB2HSV)
            satChannel = imgHSV[:, :, 1]

            if self._linearSaturation != 0:
                u = self._linearSaturation / 100.0
                if u > 0.0:
                    satChannel = (1 - u) * satChannel + u * self._saturationRange
                else:
                    satChannel = (1 + u) * satChannel

            if self._gammaSaturation != 0:
                if self._gammaSaturation > 0.0:
                    gamma = 1 + (self._gammaSaturation / 25.0)
                    satChannel = np.power(satChannel, 1 / gamma)
                elif self._gammaSaturation < 0.0:
                    gamma = 1 + (-self._gammaSaturation / 25.0)
                    satChannel = np.power(satChannel, gamma)

            imgHSV[:, :, 1] = np.clip(satChannel, 0.0, 1.0)
            imgOut = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2RGB)
            return imgOut.astype(img.dtype)

class AE_Ymean(PostProcess):
    def __init__(self,Ytarget=0.5,exposure=0.0):
        self._Ytarget = Ytarget
        self._exposureON = exposure
        self._exposureOFF = exposure
        self._on_off = True

    def setOnOff(self,on_off): self._on_off = on_off

    def setExposure(self,exposureValue):
        if self._on_off: self._exposureON = exposureValue
        else: self._exposureOFF = exposureValue

    def postProcess(self,img):
        if self._on_off: 
            ymeanb = image2Ymean(img)
            imgOut = img*(self._Ytarget/ymeanb)*math.pow(2,self._exposureON)
        else: 
            imgOut = img*math.pow(2,self._exposureOFF)
        return imgOut

class PPClip(PostProcess):
	def __int__(self,minValue=0.0,maxValue=1.0):
		self._minValue = minValue
		self._maxValue = maxValue
	def postProcess(self,imgOut):
		return np.clip(imgOut,self._minValue,self._maxValue)