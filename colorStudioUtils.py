# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""
# ----------------------------------------------------------------------------------
# import(s)
# ----------------------------------------------------------------------------------
import math
import numpy as np
import imageio
import skimage
from skimage import transform

# ----------------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------------
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
# ----------------------------------------------------------------------------------	
def loadImage(filename, scale=0.5):
    """
    load image from image filename and convert to double in [0,1]
    @params:
        filename   - Required  : image filename (Str)
        scale      - Optional  : scaling factor [=0.5] (Float)
    """
    img = imageio.imread(filename)
    imgDouble = 1.0*img/255.0
    if scale != 1.0 :
        imgDouble = skimage.transform.rescale(imgDouble, scale, anti_aliasing=True, channel_axis= 2 )
    return imgDouble
# ----------------------------------------------------------------------------------	
def image2Ymean(imgDouble):
    """
    compute Y (Luminance) mean of an image (RGB in [0,max] (Float))
    @params:
        imgDouble   - Required  : image RGB in Float
    """

    # recover image size
    x, y, c = tuple(imgDouble.shape)
    
	# color space : convert to Yuv
    # note that: XYZ assumes that RGB in [0,1], it is not the case for Yuv
    img_yuv = skimage.color.rgb2yuv(imgDouble)

	# array_like
    img_yuv_array = np.reshape(img_yuv, (x * y, c))

    # recover Y channel
    y_array = img_yuv_array[:,0]

    meanExposure = np.mean(y_array)

    return meanExposure
# ----------------------------------------------------------------------------------	
def imgRGB2chromaRG(img):
    # img RGB color space double in [0,1]
    x,y,c = img.shape
    # reshape to array
    img_array = np.reshape(img, (x * y, c))

    # rgb
    r = img_array[:,0]
    g = img_array[:,1]
    b = img_array[:,2]

    rgb_sum = r+g+b
    rgb_sum[rgb_sum == 0.0] = 1.0 # remove zeros

    rchroma = r / rgb_sum
    gchroma = g / rgb_sum

    rgchroma = np.zeros((x * y, 2))
    rgchroma[:,0] = rchroma 
    rgchroma[:,1] = gchroma 

    return rgchroma
# ----------------------------------------------------------------------------------	
def img2chromaVertices(img,scale=False):
    # img RGB color space double in [0,1]
    x,y,c = img.shape
    # reshape to array
    img_array = np.reshape(img, (x * y, c))

    # rgb
    r = img_array[:,0]
    g = img_array[:,1]
    b = img_array[:,2]

    a = np.ones(x * y)

    rgb_sum = r+g+b
    rgb_sum[rgb_sum == 0.0] = 1.0 # remove zeros

    rchroma = r / rgb_sum
    gchroma = g / rgb_sum

    if scale:
        rMax, gMax = np.amax(rchroma), np.amax(gchroma)
        rMin, gMin = np.amin(rchroma), np.amin(gchroma)
        scaling = max(rMax-rMin, gMax-gMin) 
        rchroma = (rchroma-rMin)/scaling*2.0  -1.0
        gchroma = (gchroma-gMin)/scaling*2.0  -1.0
    else:
        rchroma = rchroma*2.0  -1.0
        gchroma = gchroma*2.0  -1.0

    return np.dstack([rchroma[:], gchroma[:], r[:], g[:], b[:], a[:]])
# ----------------------------------------------------------------------------------
def colorWheel(halfSize):
	nb = halfSize*2+1
	center = halfSize
	hsv_array = np.zeros([nb,nb,3])
	for i in range(nb):
		for j in range(nb):
			ii = (i-center)/(center-1)
			jj = (j-center)/(center-1)
			r = math.sqrt(ii*ii+jj*jj)

			if (r<0.5): hsv_array[i,j,:] = [0.0,0.0,1.0]		
			elif (r<1.0):
				sat = 1.0
				hue = (math.atan2(jj,ii)+math.pi)/(2*math.pi)
				#hsv_array[i,j,:] = [hue,sat,1.0]
				hsv_array[i,j,:] = [hue,sat,1.0]
			else:
				hsv_array[i,j,:] = [0.0,0.0,0.01]

	rgb_hsv_array = skimage.color.hsv2rgb(hsv_array)        
	return rgb_hsv_array
# ----------------------------------------------------------------------------------
def inRange2D(pos,orig,size):
	xp, yp = pos[0], pos[1] 
	xo, yo = orig[0], orig[1]
	w,h = size[0], size[1]
	return ((xo<=xp)and(xp<=xo+w))and((yo<=yp)and(yp<=yo+h))