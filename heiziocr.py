import cv2
import os
import numpy as np
import re

numregex = re.compile(r'[\s\d]\d\d')

def avrg(sector):
	mean = cv2.mean(sector)[0]
	if mean < 70:
		return 0
	if mean > 135:
		return 1
	return -1

def detect(digit):
	c1 = cv2.mean(digit)[0]
	
	b1 = avrg(digit[15:20, 25:35])
	b2 = avrg(digit[30:40, 10:20])
	b3 = avrg(digit[30:40, 38:43])
	
	b4 = avrg(digit[45:55, 20:30])
	b5 = avrg(digit[60:70, 10:20])
	b6 = avrg(digit[60:70, 35:40])
	
	bs = (b1,b2,b3,b4,b5,b6)
	if c1 < 150:
		if bs == (0,1,0,1,1,0):
			return 't'
		if bs == (1,1,1,1,1,0):
			return 'p'
		if bs == (0,0,0,1,1,1):
			return 'o'
		if bs == (0,1,1,0,1,1):
			return 'u'
		if bs == (0,1,1,1,1,0):
			return 'y'
		if bs == (1,1,0,0,1,1):
			return 'g'
		if bs == (1,0,0,0,1,1):
			return 'u'
		if bs == (0,0,0,1,0,1):
			return 'u'
		if bs == (1,1,1,0,1,1):
			return '0'
		if bs == (0,0,1,0,0,1):
			return '1'
		if bs == (1,0,1,1,1,0):
			return '2'
		if bs == (1,0,1,1,0,1):
			return '3'
		if bs == (0,1,1,1,0,1):
			return '4'
		if bs == (1,1,0,1,0,1):
			return '5'
		if bs == (1,1,0,1,1,1):
			return '6'
		if bs == (1,0,1,0,0,1):
			return '7'
		if bs == (1,1,1,1,1,1):
			return '8'
		if bs == (1,1,1,1,0,1):
			return '9'
	return ' '
	
def scan(fileName, cali):
	image = cv2.imread(fileName)
	image = cv2.resize(image, (int(image.shape[1] * 500 / image.shape[0]), 500))
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.GaussianBlur(image, (25, 25), 0)
	image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 149,1)
	
	image = image[cali[0]:cali[1], cali[2]:cali[3]]
	image = cv2.resize(image, (150, 100))
	d1 = detect(image[:,0:50])
	d2 = detect(image[:,50:100])
	d3 = detect(image[:,100:150])

	result = d1+d2+d3
	return 'tag' if result == 't8g' else result
