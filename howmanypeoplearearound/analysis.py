import copy
import datetime
import json
import sys

from howmanypeoplearearound.plotlyjs import *


def analyze_file(fname, port):
    lines = []
    with open(fname, 'r') as f:
      for line in f:
        try:
          lines.append(json.loads(line))
        except:
          pass
    lines = sorted(lines, key=lambda k: k['time'])
    macs_to_add = []
    for data in lines:
        for c in data['cellphones']:
            if c['rssi'] > -80 and c['mac'] not in macs_to_add:
                macs_to_add.append(c['mac'])
    mac_data = {mac: {'y': []} for mac in macs_to_add}
    num = {'x': [], 'y': []}
    for data in lines:
        rssi = {}
        for mac in macs_to_add:
            rssi[mac] = -100
            for c in data['cellphones']:
                if c['mac'] in rssi:
                    rssi[c['mac']] = c['rssi']
        for mac in mac_data:
            mac_data[mac]['y'].append(str(rssi[mac] + 100))
        num['x'].append("'" + datetime.datetime.fromtimestamp(
            data['time']).isoformat().split('.')[0].replace('T', ' ') + "'")
        num['y'].append(str(len(data['cellphones'])))

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

    js = ""
    js += ('timex = [%s]' % ', '.join(num['x']))
    for i, mac in enumerate(macs_to_add):
        js += ('\nvar %s = {' % mac_names[i])
        js += ('\n  x: timex,')
        js += ('\n  y: [%s],' % ', '.join(mac_data[mac]['y']))
        js += ("\n name: '%s', mode: 'lines', type:'scatter' };\n\n" % mac)
    js += ('\n\nvar data = [%s];' % ', '.join(mac_names))
    js += ("\n\nPlotly.newPlot('myDiv',data,layout2);")
    js += ('\nvar num_cellphones = {')
    js += ('\n  x: timex,')
    js += ('\n  y: [%s],' % ', '.join(num['y']))
    js += ("\n name: 'N', mode: 'lines', type:'scatter' };\n\n")
    js += ("\n\nPlotly.newPlot('myDiv2',[num_cellphones],layout1);")

    with open('index.html', 'w') as f:
        f.write("""<html><head>
        <!-- Plotly.js -->
        <script type="text/javascript" src="https://cdn.plot.ly/plotly-1.27.0.min.js"></script>
    </head>

    <body>
        <div id="myDiv2" style="width: 950px; height: 350px;">
            <!-- Plotly chart will be drawn inside this DIV -->
        </div>

        <div id="myDiv" style="width: 950px; height: 350px;">
            <!-- Plotly chart will be drawn inside this DIV -->
        </div>
        <script>
var layout1 = {
  title: 'Total Count',
  xaxis: {
    title: 'date',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  },
  yaxis: {
    title: 'number',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  }
};
var layout2 = {
  title: 'Individual traces',
  xaxis: {
    title: 'date',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  },
  yaxis: {
    title: 'rssi',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  }
};
    %s
        </script>
    </body></html>""" % (js))
    print("Wrote index.html")
    print("Open browser to http://localhost:" + str(port))
    print("Type Ctl+C to exit")
    if sys.version_info >= (3, 0):
        # Python 3 code in this block
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
        httpd.serve_forever()
    else:
        # Python 2 code in this block
        import SimpleHTTPServer
        import SocketServer
        httpd = SocketServer.TCPServer(("", port), SimpleHTTPServer.SimpleHTTPRequestHandler)
        httpd.serve_forever()
