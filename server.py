#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
from heizidb import HeiziDb
import urllib.parse

def querylast():
	heizidb = None
	try:
		heizidb = HeiziDb()
		cur = heizidb.cur
		selectsql = "SELECT * FROM heizi.data WHERE key = %s ORDER BY time DESC LIMIT 1;"
		result = {}
		
		cur.execute(selectsql, ('tag',))
		row = cur.fetchone()
		result['tag'] = row[2]
		mintime = row[0]
		
		cur.execute(selectsql, ('pu',))
		row = cur.fetchone()
		result['pu'] = row[2]
		mintime = min(mintime, row[0])
		
		cur.execute(selectsql, ('po',))
		row = cur.fetchone()
		result['po'] = row[2]
		mintime = min(mintime, row[0])
		
		cur.execute(selectsql, ('ty',))
		row = cur.fetchone()
		result['ty'] = row[2]
		mintime = min(mintime, row[0])
		
		result['time'] = mintime
		
		return result
	finally:
		if heizidb is not None:
			heizidb.close()

def queryrange(mintime, maxtime):
	heizidb = None
	try:
		heizidb = HeiziDb()
		cur = heizidb.cur
		selectsql = "SELECT * FROM heizi.data WHERE time >= %s AND time <= %s ORDER BY time ASC;"
		result = {'tag': [], 'ty': [], 'po': [], 'pu': [], 'tur': []}

		cur.execute(selectsql, (mintime, maxtime,))
		for row in cur.fetchall():
			time = row[0]
			key = row[1].strip()
			value = row[2]
			if key == 'tur':
				result[key].append(time)
			elif key in result:
				dataset = [time, value]
				result[key].append(dataset)

		return result
	finally:
		if heizidb is not None:
			heizidb.close()

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
