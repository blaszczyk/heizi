#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from heizidb import HeiziDb

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
		
		cur.execute(selectsql, ('pu ',))
		row = cur.fetchone()
		result['pu'] = row[2]
		mintime = min(mintime, row[0])
		
		cur.execute(selectsql, ('po ',))
		row = cur.fetchone()
		result['po'] = row[2]
		mintime = min(mintime, row[0])
		
		cur.execute(selectsql, ('ty ',))
		row = cur.fetchone()
		result['ty'] = row[2]
		mintime = min(mintime, row[0])
		
		result['time'] = mintime
		print("queries returned %s", str(result))
		
		return result
#	except (Exception, psycopg2.DatabaseError) as error:
#		print('sqlerror', error)
	finally:
		if heizidb is not None:
			heizidb.close()

class Server(BaseHTTPRequestHandler):
	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_GET(self):
		self._set_response()
		path = str(self.path)
		response = 'Hello Heizi!'
		if path == '/latest':
			data = querylast()
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
