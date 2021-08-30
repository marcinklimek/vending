# Konfiguracja rpi w tybie kiosk:

https://itnext.io/raspberry-pi-read-only-kiosk-mode-the-complete-tutorial-for-2021-58a860474215

## Konfiguracja pinów przy boot

### Old method
[how to update device tree](https://planktonscope.readthedocs.io/en/stable/update_device-tree.html)

[shell commands](https://gist.github.com/niun/f8443db5bbfaaf02b026)

* apt-get install device-tree-compiler
* wget https://raw.githubusercontent.com/raspberrypi/firmware/master/extra/dt-blob.dts
* # for example, set P1:26 (BCM pin 7) to active low (on Raspi B Rev2.0, in dts file from August): 
* awk 'NR==104{print "                  pin@p7  { function = \"output\"; termination = \"pull_down\"; }; // SPI_CE1_N (P1:26)"}1' dt-blob.dts > dt-blob-mod.dts
* dtc -I dts -O dtb -o /boot/dt-blob.bin dt-blob-mod.dts

### a new method
	[config.txt - gpio](https://www.raspberrypi.org/documentation/computers/config_txt.html#gpio)


# HDMI display

Plik: config.txt (boot/config.txt)

overscan_left=0
overscan_right=0
overscan_top=0
overscan_bottom=0
hdmi_group=2
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=1 
max_usb_current=1

Plik: cmdline.txt   (/boot/cmdline.txt)
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty3 root=PARTUUID=04e03fbd-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait loglevel=3 quiet logo.nologo vt.global_cursor_default=0



# komunikacja

## javascript
https://github.com/pladaria/reconnecting-websocket

## python
https://pypi.org/project/websockets/
https://websockets.readthedocs.io/en/stable/index.html
https://pythonrepo.com/repo/aaugustin-websockets-python-websocket