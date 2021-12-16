import subprocess
from deployconfig import *
import sys

PROD_FILES = ['server', 'heizidb', 'detect', 'weathercrawl', 'heizibi', 'heiziocr', 'calibrate', 'healthwatch', 'dbbackup']

print('deploying to', sshtarget)
for file in PROD_FILES:
	srcpath = file + '.py'
	print('deploying', srcpath)
	subprocess.run(['scp', srcpath, sshtarget])

if len(sys.argv) > 1 and sys.argv[1] == 'reboot':
	subprocess.run(['ssh', sshhost, 'sudo reboot'])
