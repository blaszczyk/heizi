import time as timelib

ALERT = 'ALERT'
INFO = 'INFO'
ADMIN = 'ADMIN'

def attach_message(data):
	level, title, detail = message(data)
	if level:
		data['message'] = {'level':level, 'title': title, 'detail':detail}

def message(data):
	timenow = int(timelib.time())
	tag = data['tag']
	dtag = data['dtag']
	po = data['po']
	dpo = data['dpo']
	pu = data['pu']
	tur = data['tur']
	vent = data['vent']
	time = data['time']
	turAge = timenow - tur
	dataAge = timenow - time

	if dataAge > 300 and turAge > 300:
		return ADMIN, 'Detektor fehlerhaft', 'seit %d min.' % int(dataAge/60)

	if po < 60 and turAge > 300 and dtag <= 1 and tag < 150:
		tempus = 'wird' if dpo < -0.2 else 'ist'
		return ALERT, 'Speicher %s kalt' % tempus, 'Temperatur %d°C' % po

	if pu > 85 and dpu >= 0:
		return ALERT, 'Speicher heiss', 'Temperatur %d°C' % pu

	if tag > 280:
		return ALERT, 'Ofen heiss', 'Temperatur %d°C' % tag

	if tur > time:
		ventstate = 'Ventilator ' + ('an' if vent else 'aus')
		if dataAge > 1800:
			return ALERT, 'Tür auf seit %d min.' % int(dataAge/60), 'Was ist da los?'
		else:
			return INFO, 'Tuer auf ' + ventstate, ''

	return None, None, None
