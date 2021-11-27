#!/usr/bin/python3
from heizidb import transact_heizi_db

SQL_CREATE = 'CREATE SCHEMA heizi; CREATE TABLE heizi.data (time INTEGER PRIMARY KEY , key VARCHAR(3), value INTEGER );'
with transact_heizi_db() as cursor:
	cursor.execute(SQL_CREATE)
