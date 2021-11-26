import psycopg2

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
