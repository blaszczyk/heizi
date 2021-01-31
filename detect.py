#!/usr/bin/python3
from picamera import PiCamera
from time import sleep
import time
import cv2
import os
import numpy as np
import psycopg2
import re
from heizidb import HeiziDb
from heiziocr import scan
from calibrate import calibrate

numregex = re.compile(r'[\s\d]\d\d')

def persist(timestamp, key, value):
	print('persisting', timestamp, key, value)
	heizidb = None
	try:
		heizidb = HeiziDb()
		cur = heizidb.cur

		insertsql = 'INSERT INTO heizi.data VALUES (%s, %s, %s);'
		cur.execute(insertsql, (timestamp, key, value))

		heizidb.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if heizidb is not None:
			heizidb.close()

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

camera = PiCamera()
camera.rotation = 270
print('starting camera')
camera.start_preview()

cali = readCalibration()
try:
	sleep(4)
	lastkey = None
	lasttur = int(time.time())
	lasttimes = {'tag': lasttur}
	lastcalistart = None

	while True:
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
			print('detected',result)

			if result == 'tur':
				persist(timestamp, result, 0)
				lasttur = timestamp
				lasttimes = {}
			elif result == ' oo':
				lastkey = 'tag'
			elif result in ['tag', 'ty ', 'po ', 'pu ']:
				lastkey = result
			elif lastkey:
				if numregex.match(result):
					persist(timestamp, lastkey, int(result))
					lasttimes[lastkey] = timestamp
				lastkey = None

			elif timestamp - lasttur > 30:
				lasttimeall = 0
				for key, lasttime in lasttimes.items():
					lasttimeall = max(lasttime, lasttimeall)
					if timestamp - lasttime > 60:
						print('no recent ' + key + ' data. triggering calibration')
						cali = None
				if timestamp - lasttimeall > 30:
					print('no reasonable data. triggering calibration')
					cali = None
					
		if not cali:
			if not lastcalistart:
				lastcalistart = timestamp
			elif timestamp - lastcalistart > 120:
				os.remove('calibration')
				print('calibration failed for 2 minutes. terminating process.')
				break
			cali = calibrate(file)
			if cali:
				print('calibration', cali)
				lastcalistart = None
				writeCalibration(cali)
				lasttimes = {'tag': timestamp}
				lastkey = 'tag'

		if not os.path.exists('keepimg'):
			os.remove(file)

except KeyboardInterrupt:
	pass

print('stopping camera')
camera.stop_preview()
