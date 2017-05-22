import threading
import sys
import os
import platform
import subprocess
import json
import time

import netifaces
if os.name != 'nt':
    from pick import pick
import click

from howmanypeoplearearound.oui import *
from howmanypeoplearearound.analysis import *


def which(program):
    """Determines whether program exists
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    raise


def showTimer(timeleft):
    """Shows a countdown timer"""
    total = int(timeleft) * 10
    for i in range(total):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        timeleft_string = '%ds left' % int((total - i + 1) / 10)
        if (total - i + 1) > 600:
            timeleft_string = '%dmin %ds left' % (
                int((total - i + 1) / 600), int((total - i + 1) / 10 % 60))
        sys.stdout.write("[%-50s] %d%% %15s" %
                         ('=' * int(50.5 * i / total), 101 * i / total, timeleft_string))
        sys.stdout.flush()
        time.sleep(0.1)
    print("")


@click.command()
@click.option('-a', '--adapter', default='', help='adapter to use')
@click.option('-z', '--analyze', default='', help='analyze file')
@click.option('-s', '--scantime', default='60', help='time in seconds to scan')
@click.option('-o', '--out', default='', help='output cellphone data to file')
@click.option('-v', '--verbose', help='verbose mode', is_flag=True)
@click.option('--number', help='just print the number', is_flag=True)
@click.option('-j', '--jsonprint', help='print JSON of cellphone data', is_flag=True)
@click.option('-n', '--nearby', help='only quantify signals that are nearby (rssi > -70)', is_flag=True)
@click.option('--allmacaddresses', help='do not check MAC addresses against the OUI database to only recognize known cellphone manufacturers', is_flag=True)
@click.option('--nocorrection', help='do not apply correction', is_flag=True)
@click.option('--loop', help='loop forever', is_flag=True)
@click.option('--port', default=8001, help='port to use when serving analysis')
def main(adapter, scantime, verbose, number, nearby, jsonprint, out, allmacaddresses, nocorrection, loop, analyze, port):
    if analyze != '':
        analyze_file(analyze, port)
        return
    if loop:
        while True:
            scan(adapter, scantime, verbose, number,
                 nearby, jsonprint, out, allmacaddresses, nocorrection, loop)
    else:
        scan(adapter, scantime, verbose, number,
             nearby, jsonprint, out, allmacaddresses, nocorrection, loop)


def scan(adapter, scantime, verbose, number, nearby, jsonprint, out, allmacaddresses, nocorrection, loop):
    """Monitor wifi signals to count the number of people around you"""

    # print("OS: " + os.name)
    # print("Platform: " + platform.system())

    try:
        tshark = which("tshark")
    except:
        if platform.system() != 'Darwin':
            print('tshark not found, install using\n\napt-get install tshark\n')
        else:
            print('wireshark not found, install using: \n\tbrew install wireshark')
            print(
                'you may also need to execute: \n\tbrew cask install wireshark-chmodbpf')
        return

    if jsonprint:
        number = True
    if number:
        verbose = False

    if len(adapter) == 0:
        if os.name == 'nt':
            print('You must specify the adapter with   -a ADAPTER')
            print('Choose from the following: ' +
                  ', '.join(netifaces.interfaces()))
            return
        title = 'Please choose the adapter you want to use: '
        adapter, index = pick(netifaces.interfaces(), title)

    print("Using %s adapter and scanning for %s seconds..." %
          (adapter, scantime))

    if not number:
        # Start timer
        t1 = threading.Thread(target=showTimer, args=(scantime,))
        t1.daemon = True
        t1.start()

    # Scan with tshark
    command = [tshark, '-I', '-i', adapter, '-a',
               'duration:' + scantime, '-w', '/tmp/tshark-temp']
    if verbose:
        print(' '.join(command))
    run_tshark = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, nothing = run_tshark.communicate()
    if not number:
        t1.join()

    # Read tshark output
    command = [
        tshark, '-r',
        '/tmp/tshark-temp', '-T',
        'fields', '-e',
        'wlan.sa', '-e',
        'wlan.bssid', '-e',
        'radiotap.dbm_antsignal'
    ]
    if verbose:
        print(' '.join(command))
    run_tshark = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, nothing = run_tshark.communicate()
    foundMacs = {}
    for line in output.decode('utf-8').split('\n'):
        if verbose:
            print(line)
        if not line.strip():
            continue
        mac = line.split()[0].strip().split(',')[0]
        dats = line.split()
        if len(dats) == 3 and ':' in dats[0]:
            if mac not in foundMacs:
                foundMacs[mac] = []
            rssi = 0
            if len(dats[2].split(',')) > 1:
                rssi = float(dats[2].split(',')[0]) / 2 + \
                    float(dats[2].split(',')[1]) / 2
            else:
                rssi = float(dats[2].split(',')[0])
            foundMacs[mac].append(rssi)

    if not foundMacs:
        print("Found no signals, are you sure %s supports monitor mode?" % adapter)
        return
    
    for mac in foundMacs:
        foundMacs[mac] = (float(sum(foundMacs[mac])) /
            len(foundMacs[mac]))

    cellphone = [
        'Motorola Mobility LLC, a Lenovo Company',
        'GUANGDONG OPPO MOBILE TELECOMMUNICATIONS CORP.,LTD',
        'Huawei Symantec Technologies Co.,Ltd.',
        'Microsoft',
        'HTC Corporation',
        'Samsung Electronics Co.,Ltd',
        'BlackBerry RTS',
        'LG ELECTRONICS INC',
        'Apple, Inc.',
        'LG Electronics',
        'OnePlus Tech (Shenzhen) Ltd',
        'Xiaomi Communications Co Ltd',
        'LG Electronics (Mobile Communications)']

    cellphone_people = []
    for mac in foundMacs:
        oui_id = 'Not in OUI'
        if mac[:8] in oui:
            oui_id = oui[mac[:8]]
        if verbose:
            print(mac, oui_id, oui_id in cellphone)
        if allmacaddresses or oui_id in cellphone:
            if not nearby or (nearby and foundMacs[mac] > -70):
                cellphone_people.append(
                    {'company': oui_id, 'rssi': foundMacs[mac], 'mac': mac})

    if verbose:
        print(json.dumps(cellphone_people, indent=2))

    # US / Canada: https://twitter.com/conradhackett/status/701798230619590656
    percentage_of_people_with_phones = 0.7
    if nocorrection:
        percentage_of_people_with_phones = 1
    num_people = int(round(len(cellphone_people) /
                           percentage_of_people_with_phones))

    if number and not jsonprint:
        print(num_people)
    elif jsonprint:
        print(json.dumps(cellphone_people, indent=2))
    else:
        if num_people == 0:
            print("No one around (not even you!).")
        elif num_people == 1:
            print("No one around, but you.")
        else:
            print("There are about %d people around." % num_people)

    if out:
        with open(out, 'a') as f:
            data_dump = {'cellphones': cellphone_people, 'time': time.time()}
            f.write(json.dumps(data_dump) + "\n")
        if verbose:
            print("Wrote %d records to %s" % (cellphone_people, out))
    os.remove('/tmp/tshark-temp')


if __name__ == '__main__':
    main()
    # oui = {}
    # with open('data/oui.txt','r') as f:
    #     for line in f:
    #         if '(hex)' in line:
    #             data = line.split('(hex)')
    #             key = data[0].replace('-',':').lower().strip()
    #             company = data[1].strip()
    #             oui[key] = company
    # with open('oui.json','w') as f:
    #     f.write(json.dumps(oui,indent=2))
    
