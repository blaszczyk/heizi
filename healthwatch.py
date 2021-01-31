#!/usr/bin/python3
from heizidb import HeiziDb
from time import sleep
import os
import time

def querylasttime():
	heizidb = None
	try:
		heizidb = HeiziDb()
		cur = heizidb.cur
		selectsql = "SELECT * FROM heizi.data ORDER BY time DESC LIMIT 1;"
		
		cur.execute(selectsql)
		row = cur.fetchone()
		lasttime = row[0]
		return lasttime
	finally:
		if heizidb is not None:
			heizidb.close()

print('Starting health watcher...')
sleep(180)
try:
	while True:
		sleep(10)
		currenttime = int(time.time())
		lastdatatime = querylasttime()
		age = currenttime - lastdatatime
		if age > 180 and os.path.exists('calibration'):
			print('no data since 3 minutes. rebooting device.')
			os.system('sudo shutdown -r now')
		else:
			print('last data age: ' + str(age) + ' sec')
except KeyboardInterrupt:
	pass
