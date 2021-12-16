#!/usr/bin/python3
from heizidb import transact_heizi_db

SQL_CREATE_SCHEMA = 'CREATE SCHEMA heizi;'
SQL_CREATE_TABLE = 'CREATE TABLE heizi.data (time INTEGER , key VARCHAR(3), value INTEGER );'
SQL_CREATE_INDEX_TIME = 'CREATE INDEX idx_time ON heizi.data (time);'
SQL_CREATE_INDEX_KEY = 'CREATE INDEX idx_key ON heizi.data (key);'
with transact_heizi_db() as cursor:
	cursor.execute(SQL_CREATE_SCHEMA)
	cursor.execute(SQL_CREATE_TABLE)
	cursor.execute(SQL_CREATE_INDEX_TIME)
	cursor.execute(SQL_CREATE_INDEX_KEY)
