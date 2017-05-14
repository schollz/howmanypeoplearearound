
# howmanypeoplearearound 

Count the number of people around you :family_man_man_boy: by monitoring wifi signals :satellite:.

*howmanypeoplearearound* calculates the number of people in the vicinity
using the approximate number of smartphones as a proxy (since [~70% of people have smartphones nowadays](https://twitter.com/conradhackett/status/701798230619590656)). 
A cellphone is determined to be in proximity to the computer based on sniffing WiFi probe 
requests. Possible uses of *howmanypeoplearearound* include: monitoring foot traffic in your house
with Raspberry Pis, seeing if your roommates are home, etc.

Tested on Linux (Raspbian and Ubuntu) and macOS.

### **It may be illegal** to use this to monitor networks, especially ones that *you do not own*. Please check your country's laws (for US [Section 18 U.S. Code § 2511](https://www.law.cornell.edu/uscode/text/18/2511)) - [discussion](https://github.com/schollz/howmanypeoplearearound/issues/4).

Getting started
===============

## Dependencies

### WiFi adapter with monitor mode

There are a number of possible USB WiFi adapters that support monitor mode.
Personally I prefer the [TN722N](http://www.ebay.com/sch/i.html?_pgn=1&isRefine=false&_nkw=tn722n) which 
is only ~$10 and works great with every model of the Raspberry Pi. [Here is a good list of adapters that support 'ad-hoc' mode](http://elinux.org/RPi_USB_Wi-Fi_Adapters) for the
Raspberry Pi.

### [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) 

```
sudo apt-get install tshark
```

Then update it so it can be run as non-root:

```
sudo dpkg-reconfigure wireshark-common     (select YES)
sudo usermod -a -G wireshark $USER
```

You will need to logout and log back in for changes to effect.


## Install

If you have Python installed, run this command

```
pip install howmanypeoplearearound
```

## Run

First determine which adapter you want to use to scan (usually its `wlan1`), which you can find the name of using `ifconfig`. Then, to run, just type in

```bash
$ howmanypeoplearearound
Specify WiFi adapter (use ifconfig to determine): wlan1
Using wlan1 adapter and scanning for 60 seconds...
[==================================================] 100%        0s left
There are about 3 people around.
```

You can modify the scan time, designate the adapter, or modify the output using some command-line options.

```bash
$ howmanypeoplearearound --help

Options:
  -a, --adapter TEXT   adapter to use
  -s, --scantime TEXT  time in seconds to scan
  -o, --out TEXT       output cellphone data to file
  -v, --verbose        verbose mode
  --number             just print the number
  -j, --jsonprint      print JSON of cellphone data
  -n, --nearby         only quantify signals that are nearby (rssi > -70)
  --help               Show this message and exit.
```

You can also generate an JSON-formatted output to see what kind of phones are around:

```bash
$ howmanypeoplearearound -o test.json -a wlan1
[==================================================] 100%         0s left
There are about 4 people around.
$ cat test.json
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

You can create a log file with the number of people this one-liner (make sure to change your adapter):

```
$  while :; do echo "`date` `howmanypeoplearearound --number -a wlan1 -s 180`" >> log; sleep 1; done
```

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
