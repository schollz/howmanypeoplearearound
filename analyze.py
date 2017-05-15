import json
import datetime

import matplotlib.pyplot as plt

# t = []
# n = []
# with open('whoisaround.json','r') as f:
# 	for line in f:
# 		data = json.loads(line)
# 		t.append(datetime.datetime.fromtimestamp(data['time']))
# 		n.append(len(data['cellphones']))

# plt.xlabel('time')
# plt.ylabel('n')
# plt.plot(t,n,'.-')
# plt.plot(t,n,'.-')
# plt.show()


rssi = {}
with open('whoisaround.json','r') as f:
	for line in f:
		data = json.loads(line)
		for c in data['cellphones']:
			if c['mac'] not in rssi:
				rssi[c['mac']] = {'time':[],'rssi':[]}
			rssi[c['mac']]['time'].append(datetime.datetime.fromtimestamp(data['time']))
			rssi[c['mac']]['rssi'].append(c['rssi'])


plt.xlabel('time')
plt.ylabel('n')
for c in rssi:
	worthPlotting = 0
	for val in rssi[c]['rssi']:
		if val > -60:
			worthPlotting += 1
	if worthPlotting > 12:
		plt.plot(rssi[c]['time'],rssi[c]['rssi'],'.-')
plt.show()
