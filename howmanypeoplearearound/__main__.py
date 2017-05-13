import threading
import sys
import os
import subprocess
import json
import time
import datetime
import shlex

import click
# from pick import pick

from howmanypeoplearearound.oui import *


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
@click.option('-a', '--adapter', prompt='Specify WiFi adapter (use ifconfig to determine)', help='adapter to use')
@click.option('-s', '--scantime', default='60', help='time in seconds to scan')
@click.option('-o', '--out', default='', help='output cellphone data to file')
@click.option('-v', '--verbose', help='verbose mode', is_flag=True)
@click.option('--number', help='just print the number', is_flag=True)
@click.option('-j', '--jsonprint', help='print JSON of cellphone data', is_flag=True)
@click.option('-n', '--nearby', help='only quantify signals that are nearby (rssi > -70)', is_flag=True)
@click.option('--nocorrection', help='do not apply correction', is_flag=True)
def main(adapter, scantime, verbose, number, nearby, jsonprint, out, nocorrection):
    """Monitor wifi signals to count the number of people around you"""

    # Sanitize input
    adapter = shlex.quote(adapter)
    scantime = shlex.quote(scantime)

    try:
        tshark = which("tshark")
    except:
        print("tshark not found, install using\n\napt-get install tshark\n")
        return

    if jsonprint:
        number = True
    if number:
        verbose = False

    # This part requires SUDO, maybe not use it
    # adapters = []
    # for line in subprocess.check_output(
    #         ['ifconfig']).decode('utf-8').split('\n'):
    #     if ' Link' in line and line[0] == 'w':
    #         adapters.append(line.split()[0])

    # if len(adapter) == 0:
    #     title = 'Please choose the adapter you want to use: '
    #     adapter, index = pick(adapters, title)
    # if not number:
    #     print("Using %s adapter and scanning for %s seconds..." %
    #           (adapter, scantime))

    if not number:
        # Start timer
        t1 = threading.Thread(target=showTimer, args=(scantime,))
        t1.start()

    # Scan with tshark
    command = "%s -I -i %s -a duration:%s -w /tmp/tshark-temp" % (
        tshark, adapter, scantime)
    if verbose:
        print(command)
    run_tshark = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, nothing = run_tshark.communicate()
    if not number:
        t1.join()

    # Read tshark output
    command = "%s -r /tmp/tshark-temp -T fields -e wlan.sa -e wlan.bssid -e radiotap.dbm_antsignal" % tshark
    if verbose:
        print(command)
    run_tshark = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, nothing = run_tshark.communicate()
    foundMacs = {}
    for line in output.decode('utf-8').split('\n'):
        if verbose:
            print(line)
        if len(line.strip()) == 0:
            continue
        mac = line.split()[0].strip()
        if mac not in foundMacs:
            rssi = 0
            dats = line.split()
            if len(dats) == 3:
                if ':' not in dats[0]:
                    continue
                rssi = float(dats[2].split(',')[0]) / 2 + \
                    float(dats[2].split(',')[0]) / 2
                foundMacs[mac] = rssi

    if len(foundMacs) == 0:
        print("Found no signals, are you sure %s supports monitor mode?" % adapter)
        return

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
        'LG Electronics (Mobile Communications)']

    cellphone_people = []
    for mac in foundMacs:
        if mac[:8] in oui:
            oui_id = oui[mac[:8]]
            if verbose:
                print(mac, oui_id, oui_id in cellphone)
            if oui_id in cellphone:
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

    if len(out) > 0:
        with open(out, 'w') as f:
            f.write(json.dumps(cellphone_people, indent=2))
        if verbose:
            print("Wrote data to %s" % out)
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
