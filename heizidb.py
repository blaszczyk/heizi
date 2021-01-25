#!/usr/bin/python3
import psycopg2

from dbconfig import config

class HeiziDb():

	conn = None
	cur = None

	def __init__(self):
		self.conn = psycopg2.connect(**config)
		self.cur = self.conn.cursor()
		
	def close(self):
		if self.cur is not None:
			self.cur.close()
		if self.conn is not None:
			self.conn.close()

	def commit(self):
		if self.cur is not None:
			self.cur.close()
		if self.conn is not None:
			self.conn.commit()
