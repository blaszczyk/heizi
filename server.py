#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
from heizidb import query_heizi_db
from heizibi import attach_message
from weathercrawl import REPORT
import urllib.parse

SQL_SELECT_LAST_RANGE = 'SELECT time, value FROM heizi.data WHERE key = %s ORDER BY time DESC LIMIT 25;'
SQL_SELECT_LAST_TIME = 'SELECT time, value FROM heizi.data WHERE key = %s ORDER BY time DESC LIMIT 1;'
SQL_SELECT_RANGE = 'SELECT * FROM heizi.data WHERE time >= %s AND time <= %s ORDER BY time ASC;'

HEIZI_KEYS = ['tag', 'ty', 'po', 'pu']

def slope(rows):
	t0 = rows[0][0]
	n, st, sv, stt, stv = 0, 0, 0, 0, 0
	for (tfull, v) in rows:
		t = tfull - t0
		if t > -300 or n < 2:
			n += 1
			st += t
			sv += v
			stt += t*t
			stv += t*v
	return 60 * (n * stv - st * sv) / (n * stt - st * st) # degrees per minute

def evalkey(key, cursor, result):
	cursor.execute(SQL_SELECT_LAST_RANGE, (key,))
	rows = cursor.fetchall()
	firstrow = rows[0]
	result[key] = firstrow[1]
	result['d'+key] = slope(rows)
	return firstrow[0]

def querylast():
	with query_heizi_db() as cursor:
		result = {}
		
		mintimes = [evalkey(key, cursor, result) for key in HEIZI_KEYS]
		mintime = min(mintimes)
		result['time'] = mintime

		cursor.execute(SQL_SELECT_LAST_TIME, ('tur',))
		row = cursor.fetchone()
		result['tur'] = row[0]
		result['vent'] = row[1] > 0

		cursor.execute(SQL_SELECT_LAST_TIME, ('owm',))
		row = cursor.fetchone()
		result['owm'] = row[1]

		attach_message(result)
		return result

def queryrange(mintime, maxtime):
	with query_heizi_db() as cursor:
		result = {'tag': [], 'ty': [], 'po': [], 'pu': [], 'tur': [], 'owm': []}

		cursor.execute(SQL_SELECT_RANGE, (mintime, maxtime,))
		for row in cursor.fetchall():
			time = row[0]
			key = row[1].strip()
			value = row[2]
			if key in result:
				dataset = [time, value]
				result[key].append(dataset)

		return result

class Server(BaseHTTPRequestHandler):
	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()

	def do_GET(self):
		self._set_response()
		parsedpath = urllib.parse.urlparse(self.path)
		path = parsedpath.path
		query = urllib.parse.parse_qs(parsedpath.query)
		response = 'Hello Heizi!'

		if path == '/latest':
			data = querylast()
			response = json.dumps(data)

		elif path == '/range':
			maxtime = int(query['maxtime'][0]) if 'maxtime' in query else int(time.time())
			mintime = int(query['mintime'][0]) if 'mintime' in query else maxtime - 10800
			data = queryrange(mintime, maxtime)
			response = json.dumps(data)

		elif path == '/ping':
			response = '"pong"'

		self.wfile.write(bytes(response, 'utf-8'))
		

server_address = ('', 4321)
httpd = HTTPServer(server_address, Server)
print('Starting http...')
try:
	httpd.serve_forever()
except KeyboardInterrupt:
	pass
httpd.server_close()
print('Stopping http...')
