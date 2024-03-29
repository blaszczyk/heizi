#!/usr/bin/python3
from picamera import PiCamera
from time import sleep
import time
import cv2
import os
import numpy as np
import psycopg2
import re
from weathercrawl import REPORT
from heizidb import persist
from heiziocr import scan
from calibrate import calibrate

NUM_REGEX = re.compile(r'[\s\d]\d\d')

def readCalibration():
	if os.path.exists('calibration'):
		with open('calibration') as file:
			cali = file.read().split(':')
			return [int(s) for s in cali]
	else:
		return None

def writeCalibration(cali):
	with open('calibration', 'w') as file:
		file.write('%d:%d:%d:%d' % cali)

def newTimes(time):
	return {'tag': time, 'ty': time, 'po': time, 'pu': time,}

camera = PiCamera()
camera.rotation = 270
print('starting camera')
camera.start_preview()

cali = readCalibration()
try:
	sleep(4)
	lastkey = None
	lasttur = int(time.time())
	lasttimes = newTimes(lasttur)
	lastcalistart = None
	lastowm = 0

	while True:
		owmtime = REPORT['time']
		if lastowm < owmtime:
			lastowm = owmtime
			temp = round(REPORT['weather']['main']['temp'])
			persist('owm', temp)
		
		sleep(1)
		timestamp = int(time.time())
		file = 'img/' + str(timestamp) + '.jpg'
		camera.capture(file)

		if os.path.exists("calibrate"):
			os.remove('calibrate')
			print('external calibration request')
			cali = None
			
		if cali:
			result = scan(file, cali)
			print('detected', result)

			if result == ' oo': # == ' on'
				persist('tur', 1)
				lasttur = timestamp
				lasttimes = newTimes(lasttur)
				lastkey = 'tag'
			elif result == 'off':
				persist('tur', 0)
				lasttur = timestamp
				lasttimes = newTimes(lasttur)
				lastkey = 'tag'
			elif result in ['tag', 'ty ', 'po ', 'pu ']:
				lastkey = result.strip()
			elif result == ' o ':
				lastkey = 'po'
			elif result == ' u ':
				lastkey = 'pu'
			elif lastkey:
				if NUM_REGEX.match(result):
					persist(lastkey, int(result))
					lasttimes[lastkey] = timestamp
				lastkey = None

			elif timestamp - lasttur > 60:
				lasttimeall = 0
				for key, lasttime in lasttimes.items():
					lasttimeall = max(lasttime, lasttimeall)
					if timestamp - lasttime > 180:
						print('no recent' , key , 'data. triggering calibration')
						cali = None
				if timestamp - lasttimeall > 30:
					print('no reasonable data. triggering calibration')
					cali = None
					
		if not cali:
			if not lastcalistart:
				lastcalistart = timestamp
			elif timestamp - lastcalistart > 120:
				print('calibration fails since' , timestamp - lastcalistart , 'seconds.')
				sleep(300)
				lastcalistart = None
			cali = calibrate(file)
			if cali:
				print('calibration', cali)
				lastcalistart = None
				writeCalibration(cali)
				lasttimes = newTimes(timestamp)
				lastkey = 'tag'
			if not os.path.exists('keepimg'):
				os.remove(file)

		for filename in os.listdir('img'):
			age = timestamp - int(filename[:filename.index('.')])
			if age > 900:
				file = os.path.join('img', filename)
				os.remove(file)

except KeyboardInterrupt:
	pass

print('stopping camera')
camera.stop_preview()
