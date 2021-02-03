#!/usr/bin/python3
from heizidb import HeiziDb

createsql = 'CREATE SCHEMA heizi; CREATE TABLE heizi.data (time INTEGER PRIMARY KEY , key VARCHAR(3), value INTEGER );'

heizidb = None
try:
	heizidb = HeiziDb()
	cur = heizidb.cur

	cur.execute(createsql)
	heizidb.commit()
finally:
	if heizidb is not None:
		heizidb.close()
