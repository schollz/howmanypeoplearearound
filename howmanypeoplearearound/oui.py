try: #python3
    from urllib.request import urlopen
except: #python2
    from urllib2 import urlopen


def load_dictionary(file):
    oui = {}
    with open(file, 'r') as f:
        for line in f:
            if '(hex)' in line:
                data = line.split('(hex)')
                key = data[0].replace('-', ':').lower().strip()
                company = data[1].strip()
                oui[key] = company
    return oui


def download_oui(to_file):
    uri = 'http://standards-oui.ieee.org/oui/oui.txt'
    print("Trying to download current version of oui.txt from [%s] to file [%s]" % (uri, to_file))
    oui_data = urlopen(uri, timeout=10).read()
    with open(to_file, 'wb') as oui_file:
        oui_file.write(oui_data)
