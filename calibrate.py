import cv2
import numpy as np

roottemplate = cv2.imread('tagref.bmp')
roottemplate = cv2.cvtColor(roottemplate, cv2.COLOR_BGR2GRAY)
rtx, rty = roottemplate.shape[1], roottemplate.shape[0]

def findtemplate(image, scale):
	template = cv2.resize(roottemplate, (int(scale*rtx), int(scale*rty)))
	res = cv2.matchTemplate(image,template, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	x1, x2, y1, y2 = max_loc[1], max_loc[1] + template.shape[0], max_loc[0], max_loc[0] + template.shape[1]
	print(scale, max_val)
	return max_val , ( x1, x2, y1, y2 )

def riseup(image, initscale, initacc, initcali, step):
	refacc, refcali = initacc, initcali
	scale = initscale
	while True:
		scale += step
		acc, cali = findtemplate(image, scale)
		if acc > refacc:
			refacc, refcali = acc, cali
		else:
			return scale - step, refacc, refcali


def calibrate(fileName):
	image = cv2.imread(fileName)
	image = cv2.resize(image, (int(image.shape[1] * 500 / image.shape[0]), 500))
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.GaussianBlur(image, (25, 25), 0)
	image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 149,1)
	
	acc, cali = findtemplate(image, 1)
	scale = 1
	if acc > 0.6:
		scale, acc, cali = riseup(image, scale, acc, cali, 0.05)
		scale, acc, cali = riseup(image, scale, acc, cali, -0.05)
		scale, acc, cali = riseup(image, scale, acc, cali, 0.01)
		scale, acc, cali = riseup(image, scale, acc, cali, -0.01)
		if acc > 0.9:
			return cali
	return None
