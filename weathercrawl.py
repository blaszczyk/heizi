import http.client
import json
import urllib
import datetime
from owmconfig import *
import time
from threading import Thread
from heizidb import transact_heizi_db

INTERVAL = 600

INSERT_SQL = 'INSERT INTO heizi.data VALUES (%s, %s, %s);'

#PATHS = ['weather', 'forecast']
PATHS = ['weather']

report = {}
for path in PATHS:
	report[path] = {}

def request(path):
	connection = http.client.HTTPSConnection('api.openweathermap.org')

	try:
		headers = { 'Accept': 'application/json' }
		query = { 'appid': OWM_API_KEY, 'lat': LATITUDE, 'lon': LONGITUDE, 'units': 'metric'}
		fullpath = '/data/2.5/' + path + '?' + urllib.parse.urlencode(query)
#		print('requesting GET@' + fullpath)
		connection.request('GET', fullpath, None, headers)
		response = connection.getresponse()
		status = response.status
#		print('response %s' % status)
		data = response.read().decode('utf-8')
		if status > 399:
			print('request failed for', fullpath)
			print('error message: ' + data)
			raise Exception('http response error')
		return json.loads(data)

	finally:
		connection.close()

def printitem(item):
	temp = item['main']['temp']
	date = datetime.datetime.fromtimestamp(item['dt']).strftime("%b %d %Y %H:%M:%S")
	print('temparature %f degrees at %s' % (temp, date))

def printreport():
	print('report from', datetime.datetime.fromtimestamp(time.time()).strftime("%b %d %Y %H:%M:%S"))
	printitem(report['weather'])
#	for item in report['forecast']['list']:
#		printitem(item)
	
def fetchreport():
	for path in PATHS:
		response = request(path)
		report[path] = response

def persist_temerature():
	temp = round(report['weather']['main']['temp'])
	print('persisting hof', temp)
	with transact_heizi_db() as cursor:
		cursor.execute(INSERT_SQL, (time.time(), 'hof', temp))
	
	
def crawl():
	nexttime = time.time()
	while True:
		fetchreport()
		persist_temerature()
#		printreport()

		nexttime += INTERVAL
		time.sleep(nexttime - time.time())

Thread(target=crawl, daemon=True).start()

if __name__ == '__main__':
	running = True
	while running:
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			print('Crawler Interrupted')
			running = False
