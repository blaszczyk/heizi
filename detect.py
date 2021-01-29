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


call = None
with open('callibration') as file:
	call = file.read(call).split(':')
	call = [int(s) for s in call]


camera = PiCamera()
camera.rotation = 270
print('starting camera')
camera.start_preview()

try:
	sleep(4)
	lastkey = None

	while True:
		sleep(1)
		timestamp = int(time.time())
		file = 'img/' + str(timestamp) + '.jpg'
		camera.capture(file)
		result = scan(file, call)
		print('detected',result)
		if result in ['tag', 'ty ', 'po ', 'pu ', 'tur']:
			lastkey = result
		elif lastkey:
			if numregex.match(result):
				persist(timestamp, lastkey, int(result))
			lastkey = None
		if not os.path.exists("keepimg"):
			os.remove(file)

except KeyboardInterrupt:
	pass

print('stopping camera')
camera.stop_preview()
