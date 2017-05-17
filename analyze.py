import json
import time
import datetime
import copy

macs_to_add = []
with open('whoisaround.json', 'r') as f:
    for line in f:
        data = json.loads(line)
        for c in data['cellphones']:
            if c['rssi'] > -80 and c['mac'] not in macs_to_add:
                macs_to_add.append(c['mac'])

print(macs_to_add)
mac_data = {}
for mac in macs_to_add:
    mac_data[mac] = {'x': [], 'y': []}

with open('whoisaround.json', 'r') as f:
    for line in f:
        data = json.loads(line)
        rssi = {}
        for mac in macs_to_add:
            rssi[mac] = -100
            for c in data['cellphones']:
                if c['mac'] in rssi:
                    rssi[c['mac']] = c['rssi']
        for mac in mac_data:
            mac_data[mac]['x'].append("'" + datetime.datetime.fromtimestamp(
                data['time']).isoformat().split('.')[0].replace('T', ' ') + "'")
            mac_data[mac]['y'].append(str(rssi[mac] + 100))

mac_names = copy.deepcopy(macs_to_add)
for i, mac in enumerate(mac_names):
    mac_names[i] = 'mac' + mac.replace(':', '')

# remove pings
for mac in mac_data:
    for i, y in enumerate(mac_data[mac]['y']):
        if y == "0" and i > 2:
            if mac_data[mac]['y'][i - 3] == "0" and (mac_data[mac]['y'][i - 1] != "0" or mac_data[mac]['y'][i - 2] != "0"):
                mac_data[mac]['y'][i - 1] = "0"
                mac_data[mac]['y'][i - 2] = "0"

with open('data.js', 'w') as f:
    for i, mac in enumerate(macs_to_add):
        f.write('\nvar %s = {' % mac_names[i])
        f.write('\n  x: [%s],' % ', '.join(mac_data[mac]['x']))
        f.write('\n  y: [%s],' % ', '.join(mac_data[mac]['y']))
        f.write("\n name: '%s', mode: 'lines', type:'scatter' };\n\n" % mac)
    f.write('\n\nvar data = [%s];' % ', '.join(mac_names))
    f.write("\n\nPlotly.newPlot('myDiv',data);")
# import matplotlib.pyplot as plt

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

# rssi = {}
# with open('whoisaround.json','r') as f:
# 	for line in f:
# 		data = json.loads(line)
# 		for c in data['cellphones']:
# 			if c['mac'] not in rssi:
# 				rssi[c['mac']] = {'time':[],'rssi':[]}
# 			rssi[c['mac']]['time'].append(datetime.datetime.fromtimestamp(data['time']))
# 			rssi[c['mac']]['rssi'].append(c['rssi'])

# plt.xlabel('time')
# plt.ylabel('n')
# for c in rssi:
# 	worthPlotting = 0
# 	for val in rssi[c]['rssi']:
# 		if val > -60:
# 			worthPlotting += 1
# 	if worthPlotting > 12:
# 		plt.plot(rssi[c]['time'],rssi[c]['rssi'],'.-')
# plt.show()
