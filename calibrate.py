import cv2
import numpy as np

tagref = cv2.cvtColor(cv2.imread('tagref.bmp'), cv2.COLOR_BGR2GRAY)
turref = cv2.cvtColor(cv2.imread('turref.bmp'), cv2.COLOR_BGR2GRAY)

def findtemplate(image, ref, scale):
	template = cv2.resize(ref, (int(scale*ref.shape[1]), int(scale*ref.shape[0])))
	res = cv2.matchTemplate(image,template, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	x1, x2, y1, y2 = max_loc[1], max_loc[1] + template.shape[0], max_loc[0], max_loc[0] + template.shape[1]
	print(scale, max_val)
	return max_val , ( x1, x2, y1, y2 )

def riseup(image, ref, initscale, initacc, initcali, step):
	refacc, refcali = initacc, initcali
	scale = initscale
	while True:
		scale += step
		acc, cali = findtemplate(image, ref, scale)
		if acc > refacc:
			refacc, refcali = acc, cali
		else:
			return scale - step, refacc, refcali

def checkscales(image, ref):
	acc, cali = findtemplate(image, ref, 1)
	scale = 1.1
	if acc > 0.35:
		scale, acc, cali = riseup(image, ref, scale, acc, cali, 0.05)
		scale, acc, cali = riseup(image, ref, scale, acc, cali, -0.05)
		scale, acc, cali = riseup(image, ref, scale, acc, cali, 0.01)
		scale, acc, cali = riseup(image, ref, scale, acc, cali, -0.01)
		if acc > 0.9:
			return cali
	return None

def calibrate(fileName):
	image = cv2.imread(fileName)
	image = cv2.resize(image, (int(image.shape[1] * 500 / image.shape[0]), 500))
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.GaussianBlur(image, (25, 25), 0)
	image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 149,1)
	
	tagcali = checkscales(image, tagref)
	return tagcali if tagcali else checkscales(image, turref)
