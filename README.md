
# howmanypeoplearearound :family_man_man_boy:

<p align="center">Monitor wifi signals :satellite: to quantify the number of people in a location</a></p>

*howmanypeoplearearound* calculates the number of people in the vicinity
using the approximate number of cellphones a proxy (since 85-95% of people have cellphones nowadays). 
A cellphone is determined to be in proximity to the computer based on sniffing WiFi probe 
requests. Possible uses of *howmanypeoplearearound* include: monitoring foot traffic in an area
with Raspberry Pis, seeing if your roommates are home, calculate how many people are on the bus, etc.

Currently tested on Linux (Raspbian and Ubuntu) only (send a PR if for OS X if you are so kind!).

Getting started
===============

## Dependencies

### WiFi adapter with monitor mode

There are a number of possible adapters that support monitor mode.
Personally I prefer the [TN722N](http://www.ebay.com/sch/i.html?_pgn=1&isRefine=false&_nkw=tn722n) which 
is only ~$10 and works great with every model of the Raspberry Pi. [Here is a good list of adapters that support 'ad-hoc' mode](http://elinux.org/RPi_USB_Wi-Fi_Adapters) for the
Raspberry Pi.

### [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) 

```
sudo apt-get install tshark 
```

## Install

If you have Python installed, run this command

```
pip install howmanypeoplearearound
```

## Run

To run, just type in

```bash
$ howmanypeoplearearound

Using wlx98ded0151d38 adapter and scanning for 5 seconds...
[==================================================] 100%        0s left
No one around but you.
```

You can modify the scan time, designate the adapter, or modify the output using some command-line options.

```bash
$ howmanypeoplearearound --help

Options:
  -a, --adapter TEXT   adapter to use
  -s, --scantime TEXT  time in seconds to scan
  -o, --out TEXT       output JSON of cellphone data to file
  -v, --verbose        verbose mode
  --number             just print the number
  -j, --jsonprint      just print the json
  -n, --nearby         only quantify signals that are nearby
  --help               Show this message and exit.
```

How does it work?
==================

*howmanypeoplearearound* counts up the number of probe requests coming from cellphones in a given amount of time.
The probe requests can be "sniffed" from a monitor-mode enabled WiFi adapter using `tshark`. An acccurate count does 
depend on everyone having cellphone and also scanning long enough (1 - 10 minutes) to capture the packet when 
a phone pings the WiFi network (which happens every 1 to 10 minutes unless the phone is off or WiFi is disabled).

License
=======

MIT
