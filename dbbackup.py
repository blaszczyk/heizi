#!/usr/bin/python3
from time import time
import subprocess

dumpfilename = 'dbdump/heizi_dump_%d.csv' % int(time())
print('dumping into', dumpfilename)
psql = "\copy heizi.data to %s csv header" % dumpfilename
subprocess.run(['psql', '-d', 'heizi', '-c', psql])
