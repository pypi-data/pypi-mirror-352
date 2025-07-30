========
rtcirqus
========

Introduction
------------

rtcirqus, real-time config IRQ udev service, is a Python script that sets the
real-time priority of IRQ threads of onboard and USB audio interfaces
automatically using udev. It is heavily inspired by Joakim Hernberg's `udev-rtirq
<https://github.com/jhernberg/udev-rtirq/>`_
project.

Features
--------
- Automatic real-time prioritization of onboard audio devices
- Automatic real-time prioritization of USB audio devices upon connection and
  disconnection

Installation
------------
rtcirqus needs at least Python 3.6 and the following Python modules:

- pyalsaaudio
- psutil
- pyudev

On a Debian 12 system these modules can be installed with
``apt install python3-alsaaudio python3-psutil python3-pyudev``

Clone this repository:

::

  git clone https://codeberg.org/autostatic/rtcirqus.git

Copy ``src/rtcirqus/rtcirqus.py`` to ``/usr/local/bin/rtcirqus``:

::

  sudo cp src/rtcirqus/rtcirqus.py /usr/local/bin/rtcirqus
  sudo chmod 755 /usr/local/bin/rtcirqus

Copy ``resources/99-rtcirqus.rules`` to ``/etc/udev/rules.d/``:

::

  sudo cp resources/99-rtcirqus.rules /etc/udev/rules.d/

And reload the udev rules:

::

  sudo udevadm control --reload-rules

Optionally you could copy ``rtcirqus.conf`` to ``/etc/rtcirqus.d/rtcirqus.conf``:

::

  sudo mkdir /etc/rtcirqus.d/
  sudo cp resources/rtcirqus.conf /etc/rtcirqus.d/conf

And modify it to your needs. So far only the ``deny_list`` option is available.
This option takes a comma separated list of card names as produced  by
``rtcirqus`` itself or by ``cat /proc/asound/cards``. In the case of
``/proc/asound/cards`` the card names are the names between the brackets.


Installation in a Virtual Environment
-------------------------------------

To install the ``rtcirqus`` project in a Python virtual environment for development:

::

  cd /path/to/clone/of/rtcirqus
  python3.9 -m venv /path/to/venv  # Python >= 3.9
  /path/to/venv/bin/pip install -e .

``pip`` will install the dependencies, and create a script, ``rtcirqus`` in its
``bin/`` directory, which you can run directly:

::

  /path/to/venv/bin/rtcirqus --help


You can then copy that script to ``/usr/local/bin/rtcirqus``:

::

  sudo cp /path/to/venv/bin/rtcirqus /usr/local/bin/

and proceed as above, adding ``udev`` rules and copying / updating configuration.


Overview
--------
You can now check if rtcirqus works properly by running it as a normal user. It
will produce output similar to the following:

::

  $ rtcirqus 
  WARNING: No configuration file found, continuing with defaults
  INFO: Loaded kernel is using threaded IRQS and threaded IRQ processes detected
  INFO: Onboard cards found: HD-Audio Generic, HD-Audio Generic, acp63
  INFO: USB cards found: Babyface (23596862)
  ERROR: Not running as root, rtcirqus needs to be run as root in order to set IRQ priorities

You can check if rtcirqus gets triggered by udev by plugging in a USB device
while running ``sudo journalctl -f``. You should see something in the lines of:

::

  Feb 16 22:34:10 lenovo kernel: usb 7-1: new high-speed USB device number 10 using xhci_hcd
  Feb 16 22:34:11 lenovo kernel: usb 7-1: New USB device found, idVendor=0424, idProduct=3fb7, bcdDevice= 0.01
  Feb 16 22:34:11 lenovo kernel: usb 7-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
  Feb 16 22:34:11 lenovo kernel: usb 7-1: Product: Babyface (23596862)
  Feb 16 22:34:11 lenovo kernel: usb 7-1: Manufacturer: RME
  Feb 16 22:34:11 lenovo kernel: usb 7-1: SerialNumber: 18C0A73560538C8
  Feb 16 22:34:11 lenovo kernel: usb 7-1: Quirk or no altest; falling back to MIDI 1.0
  Feb 16 22:34:11 lenovo mtp-probe[15199]: checking bus 7, device 10: "/sys/devices/pci0000:00/0000:00:08.3/0000:66:00.4/usb7/7-1"
  Feb 16 22:34:11 lenovo mtp-probe[15199]: bus: 7, device: 10 was not an MTP device
  Feb 16 22:34:11 lenovo systemd[1]: Started run-r4c9e3d2d062846ecab03c6af31529349.service - /usr/local/bin/rtcirqus --action add --dev-path /devices/pci0000:00/0000:00:08.3/0000:66:00.4/usb7/7-1/7-1:1.0/sound/card0.
  Feb 16 22:34:11 lenovo mtp-probe[15216]: checking bus 7, device 10: "/sys/devices/pci0000:00/0000:00:08.3/0000:66:00.4/usb7/7-1"
  Feb 16 22:34:11 lenovo mtp-probe[15216]: bus: 7, device: 10 was not an MTP device
  Feb 16 22:34:11 lenovo rtcirqus[15212]: WARNING: No configuration file found, continuing with defaults
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: Loaded kernel is using threaded IRQs and threaded IRQ processes detected
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: Onboard cards found: HD-Audio Generic, HD-Audio Generic, acp63
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: USB cards found: Babyface (23596862)
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: Setting RT priority 90 for USB card Babyface (23596862)
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: Setting RT priority 85 for onboard card HD-Audio Generic
  Feb 16 22:34:11 lenovo rtcirqus[15212]: INFO: Setting RT priority 80 for onboard card HD-Audio Generic
  Feb 16 22:34:11 lenovo systemd[1]: run-r4c9e3d2d062846ecab03c6af31529349.service: Deactivated successfully.

Future plans
------------
- Add more options to ``rtcirqus.conf`` (max_prio, min_prio, prio_step)
- Improve handling of MIDI USB devices
- Improve handling of USB devices connected to USB2 ports using the ehci_hcd kernel module
- Add option to choose between static mode and dynamic mode
  
  - static mode: priorities of connected devices stay the same upon connection
    or disconnection of devices
  - dynamic mode: priorities of connected devices get reinitialized upon
    connection or disconnection of devices 
- Think of a logo

Contact
-------

To contact me send me a mail or if it's a technical issue or question, use 
the project's issue tracker at `codeberg.org
<https://codeberg.org/autostatic/rtcirqus/issues>`_
.
