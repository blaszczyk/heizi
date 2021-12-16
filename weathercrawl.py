import http.client
import json
import urllib
import datetime
from owmconfig import *
import time
from threading import Thread

INTERVAL = 600

PATHS = ['weather', 'forecast']

REPORT = {'time': 0}
for path in PATHS:
	REPORT[path] = {}

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
			print('status: ' + status)
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
	printitem(REPORT['weather'])
	for item in REPORT['forecast']['list']:
		printitem(item)
	
def fetchreport():
	REPORT['time'] = time.time()
	for path in PATHS:
		response = request(path)
		REPORT[path] = response

def crawl():
	nexttime = time.time()
	while True:
		try:
			fetchreport()
			printreport()
			
			currenttime = time.time()
			while(nexttime < currenttime):
				nexttime += INTERVAL
			time.sleep(nexttime - currenttime)
		except Exception as e:
			print(e)
			time.sleep(5)

Thread(target=crawl, daemon=True).start()

if __name__ == '__main__':
	running = True
	while running:
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			print('Crawler Interrupted')
			running = False
