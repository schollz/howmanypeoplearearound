import threading
import sys
import os
import subprocess
import json 
import time
import datetime

import humanize
import click
from pick import pick

def which(program):
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
    total = int(timeleft)*10
    for i in range(total):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        timeleft_string = humanize.naturaltime(datetime.datetime.now() - datetime.timedelta(seconds=(total-i+1)/10))
        timeleft_string = ' '.join(timeleft_string.split()[:2])
        sys.stdout.write("[%-50s] %d%% %s left" % ('='*int(50.5*i/total), 101*i/total,timeleft_string))
        sys.stdout.flush()
        time.sleep(0.1)

@click.command()
@click.option('-a','--adapter', default='', help='adapter to use')
@click.option('-v','--verbose', help='verbose mode', is_flag=True)
@click.option('-s','--scantime', default='60', help='time in seconds to scan')
def find_people(adapter,scantime,verbose):
    """Uses tshark to determine approximately how many people are around"""
    try:
        tshark = which("tshark")
    except:
        print("tshark not found, you must install using\n\napt-get install tshark")
        return

    adapters = []
    for line in subprocess.check_output(['ifconfig']).decode('utf-8').split('\n'):
        if ' Link' in line and line[0] == 'w':
            adapters.append(line.split()[0])
    if len(adapter) == 0:
        title = 'Please choose the adapter you want to use: '
        adapter, index = pick(adapters, title)
    print("Using %s adapter and scanning for %s seconds..." % (adapter,scantime))
    # Start timer 
    t1 = threading.Thread(target=showTimer,args=(scantime,))
    t1.start()

    # Scan with tshark
    command = "%s -I -i %s -a duration:%s -w /tmp/tshark-temp" % (tshark,adapter,scantime)
    run_tshark = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, nothing = run_tshark.communicate()   
    t1.join()

    # Read tshark output
    command = "%s -r /tmp/tshark-temp -T fields -e wlan.sa -e wlan.bssid -e radiotap.dbm_antsignal" % tshark
    run_tshark = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, nothing = run_tshark.communicate()   
    oui = json.load(open('data/oui.json','r'))
    foundMacs = []
    for line in output.decode('utf-8').split('\n'):
        if verbose:
            print(line)
        if len(line.strip()) == 0:
            continue
        mac = line.split()[0].strip()
        if mac not in foundMacs:
            foundMacs.append(mac)

    num_cellphones = 0
    cellphone = ['Motorola Mobility LLC, a Lenovo Company','GUANGDONG OPPO MOBILE TELECOMMUNICATIONS CORP.,LTD','Huawei Symantec Technologies Co.,Ltd.','Microsoft','HTC Corporation','Samsung Electronics Co.,Ltd','BlackBerry RTS','LG ELECTRONICS INC','Apple, Inc.','LG Electronics','LG Electronics (Mobile Communications)']
    for mac in foundMacs:
        if mac[:8] in oui:
            oui_id = oui[mac[:8]]
            if verbose:
                print(mac,oui_id,oui_id in cellphone)
            if oui_id in cellphone:
                num_cellphones += 1

    percentage_of_people_with_phones = 0.84
    num_people = int(round(num_cellphones/percentage_of_people_with_phones))
    if num_people == 0:
        print("\n\nNo one around but you.\n\n")
    else:
        print("\n\nThere are about %d people around.\n\n" % num_people)

if __name__ == '__main__':
    find_people()
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