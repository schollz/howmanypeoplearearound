
# howmanypeoplearearound 

Count the number of people around you :family_man_man_boy: by monitoring wifi signals :satellite:.

*howmanypeoplearearound* calculates the number of people in the vicinity
using the approximate number of smartphones as a proxy (since [~70% of people have smartphones nowadays](https://twitter.com/conradhackett/status/701798230619590656)). 
A cellphone is determined to be in proximity to the computer based on sniffing WiFi probe 
requests. Possible uses of *howmanypeoplearearound* include: monitoring foot traffic in your house
with Raspberry Pis, seeing if your roommates are home, etc.

Tested on Linux (Raspbian and Ubuntu) and Mac OS X.

### **It may be illegal** to monitor networks for MAC addresses, especially on networks that *you do not own*. Please check your country's laws (for US [Section 18 U.S. Code § 2511](https://www.law.cornell.edu/uscode/text/18/2511)) - [discussion](https://github.com/schollz/howmanypeoplearearound/issues/4).

Getting started
===============

## Docker alternative

If Docker is installed locally and you want to take *howmanypeoplearearound* out for a quick spin, you can try the following:
1. Copy Dockerfile from this repo in your current working directory
2. `docker build -t howmanypeoplearearound .`  # that . at the end is important
3. `docker run -it --net=host --name howmanypeoplearearound howmanypeoplearearound`

NOTE: This is known to work on Ubuntu but *not* on Mac OS X.  Feedback on other platforms would be appreciated.

## Dependencies

Python 2.7 or preferably Python 3 must be installed on your machine with the `pip` command also available.
```
  python -V
  pip -V
```

### WiFi adapter with monitor model

There are a number of possible USB WiFi adapters that support monitor mode.
Personally I prefer the [TN722N](http://www.ebay.com/sch/i.html?_pgn=1&isRefine=false&_nkw=tn722n) which 
is only ~$10 and works great with every model of the Raspberry Pi. [Here is a good list of adapters that support 'ad-hoc' mode](http://elinux.org/RPi_USB_Wi-Fi_Adapters) for the
Raspberry Pi.

### Mac OS X
```
  brew install wireshark
  brew cask install wireshark-chmodbpf
```

### Linux [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) 
```
sudo apt-get install tshark
```

Then update it so it can be run as non-root:
```
sudo dpkg-reconfigure wireshark-common     (select YES)
sudo usermod -a -G wireshark ${USER:-root}
newgrp wireshark
```

## Install
```
pip install howmanypeoplearearound
```

## Run

### Quickstart

To run, simply type in
```bash
$ howmanypeoplearearound
Using wlan1 adapter and scanning for 60 seconds...
[==================================================] 100%        0s left
There are about 3 people around.
```

You will be prompted for the WiFi adapter to use for scanning. Make sure to use
an adapter that supports "monitor" mode.

#### Options

You can modify the scan time, designate the adapter, or modify the output using some command-line options.
```bash
$ howmanypeoplearearound --help

Options:
  -a, --adapter TEXT   adapter to use
  -z, --analyze TEXT   analyze file
  -s, --scantime TEXT  time in seconds to scan
  -o, --out TEXT       output cellphone data to file
  -v, --verbose        verbose mode
  --number             just print the number
  -j, --jsonprint      print JSON of cellphone data
  -n, --nearby         only quantify signals that are nearby (rssi > -70)
  --nocorrection       do not apply correction
  --loop               loop forever
  --sort               sort cellphone data by distance (rssi)
```

### Print JSON

You can generate an JSON-formatted output to see what kind of phones are around:
```bash
$ howmanypeoplearearound -o test.json -a wlan1
[==================================================] 100%         0s left
There are about 4 people around.
$ cat test.json | python3 -m json.tool
[
  {
    "rssi": -86.0,
    "mac": "90:e7:c4:xx:xx:xx",
    "company": "HTC Corporation"
  },
  {
    "rssi": -84.0,
    "mac": "80:e6:50:xx:xx:xx",
    "company": "Apple, Inc."
  },
  {
    "rssi": -49.0,
    "mac": "ac:37:43:xx:xx:xx",
    "company": "HTC Corporation"
  }
]
```

A higher rssi means closer (one of these phones is mine, and the other two are my roommates' who were upstairs). 

### Run forever

You can add `--loop` to make this run forever and append new lines an output file, `test.json`:
```bash
$ howmanypeoplearearound -o test.json -a wlan1 --loop
```

### Visualize 

You can visualize the output from a looped command via a browser using:
```bash
$ howmanypeoplearearound --analyze test.json 
Wrote index.html
Open browser to http://localhost:8001
Type Ctl+C to exit
```

Then just open up `index.html` in a browser and you should see plots. The first plot shows the number of people over time. Here you can see that people start arriving at work place around 8-9am (when work starts!).

![newplot](https://cloud.githubusercontent.com/assets/6550035/26174159/b478b764-3b0b-11e7-9600-2aa215b789d0.png)

The second plot shows the RSSI values for the mac addresses seen. You can double-click on one of them in particular to highlight that trajectory, as I have done here for my phone (you can see when I leave from and when I arrive to work!):

![newplot 1](https://cloud.githubusercontent.com/assets/6550035/26174160/b4911ae8-3b0b-11e7-93b2-92c3efaa01aa.png)


How does it work?
==================

*howmanypeoplearearound* counts up the number of probe requests coming from cellphones in a given amount of time.
The probe requests can be "sniffed" from a monitor-mode enabled WiFi adapter using `tshark`. An acccurate count does 
depend on everyone having cellphone and also scanning long enough (1 - 10 minutes) to capture the packet when 
a phone pings the WiFi network (which happens every 1 to 10 minutes unless the phone is off or WiFi is disabled).

This is a simplification of another program I wrote, [find-lf](https://github.com/schollz/find-lf) which uses a similar idea with a cluster of Raspberry Pis to geolocate positions of cellphones within the vicinity.

License
=======

MIT
