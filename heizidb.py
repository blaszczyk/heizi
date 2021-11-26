import psycopg2
from time import time
from dbconfig import config
from contextlib import contextmanager

@contextmanager
def query_heizi_db():
	connection = psycopg2.connect(**config)
	cursor = connection.cursor()
	
	try:
		yield cursor
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		cursor.close()
		connection.close()

@contextmanager
def transact_heizi_db():
	connection = psycopg2.connect(**config)
	cursor = connection.cursor()
	
	try:
		yield cursor
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		cursor.close()
		connection.commit()
		connection.close()

INSERT_SQL = 'INSERT INTO heizi.data VALUES (%s, %s, %s);'
def persist(key, value):
	timestamp = int(time())
	print('persisting', timestamp, key, value)
	with transact_heizi_db() as cursor:
		cursor.execute(INSERT_SQL, (timestamp, key, value))