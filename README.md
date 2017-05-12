
<p align="center">
<img
    src="logo.png"
    width="260" height="80" border="0" alt="howmanypeoplearearound">
<br>
<!--<img src="https://img.shields.io/badge/python-3.3%2B-brightgreen.svg?style=flat-square" alt="Python version">-->
</p>

<p align="center">Using tshark to quantify the number of people in a location</a></p>

*howmanypeoplearearound* is a fancy `tshark` wrapper to count the number of cellphones in the vicinity
which is used as a proxy for the number of people (since 85-95% of people have cellphones nowadays).

Getting started
===============

## Dependencies

Make sure you have Python3.3+.

### [ffmpeg](https://ffmpeg.org/download.html)

#### Mac
```
brew install ffmpeg
```

#### Ubuntu
```
sudo apt-get install ffmpeg
```

#### Windows
[Download](https://ffmpeg.org/download.html)

## Install

If you have python3.3+ installed, run this command

```
pip install playlistfromsong
```

Or use `pip3` instead of `pip` to install it with python3.

## Run

```bash
playlistfromsong --song 'Miles Davis Blue In Green'
```

![](http://i.imgur.com/ldVHZcc.gif)

You can also use Spotify if you provide a Bearer token (which [you can get here](https://developer.spotify.com/web-api/console/get-track/)):

![](http://i.imgur.com/uzEEEFh.gif)

You can also set the spotify bearer token

```
playlistfromsong config --open
```

That command will open the config file with default application.

Edit the config file and add following entry

    spotify_bearer_token: <your spotify bearer token>

change `<your spotify bearer token>` with actual token and save.

After editing the config file, everytime you use the program that token will be loaded.

You can also download a single song with

```bash
playlistfromsong --song 'Miles Davis Blue In Green' -n 1
```

# howmanypeoplearearound
Using tshark to quantify the number of people in a location
A tshark wrapper to count the number of cellphones in the vicinity