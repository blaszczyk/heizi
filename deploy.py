import subprocess
from deployconfig import sshtarget

prod_files = ['server', 'heizidb', 'detect', 'weathercrawl', 'heizibi', 'heiziocr', 'calibrate', 'healthwatch']

print('deploying to', sshtarget)
for file in prod_files:
	srcpath = file + '.py'
	print('deploying', srcpath)
	subprocess.run(['scp', srcpath, sshtarget])
