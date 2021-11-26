#!/usr/bin/python3
from heizidb import query_heizi_db
from time import sleep
import os
import time

SQL_SELECT_LAST = "SELECT * FROM heizi.data ORDER BY time DESC LIMIT 1;"

def querylasttime():
	with query_heizi_db() as cursor:
		cursor.execute(SQL_SELECT_LAST)
		row = cursor.fetchone()
		lasttime = row[0]
		return lasttime

print('Starting health watcher...')
sleep(180)
try:
	while True:
		sleep(10)
		currenttime = int(time.time())
		lastdatatime = querylasttime()
		age = currenttime - lastdatatime
		if age > 180:
			print('no data since 3 minutes. rebooting device.')
			os.system('sudo shutdown -r now')
		else:
			print('last data age', age, 'sec')
except KeyboardInterrupt:
	pass
