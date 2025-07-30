__Table of Contents__

[[_TOC_]]

# 1. Introduction

__Modbus Scale Server__ provides the server-side capabilities required by the
Mazzer and Rancilio weigh scales of project [UC-02-2024][uc-02-2024-gitlab]
_Coffee Cart Modifications_.

A [Raspberry Pi 4 Model B][raspberry-pi-4-model-b] hosts the Modbus Ethernet
server daemon that Modbus clients may query to obtain the current scale weight
(grams), or tare (zero) the scale. The daemon updates the scale weight at a
frequency of 10Hz.

The daemon uses non-privileged port 2593, which is unofficially assigned to
Ultima Online servers. This port has been chosen as use of official Modbus port
502 would require elevated user privileges.

# 2. Preparation

The Raspberry Pi communicates with the downstream [Arduino Uno][arduino-uno]
using the two-wire serial I2C (_Inter-Integrated Circuit_) protocol.
Unfortunately I2C communications are not enabled by default within the
Raspberry Pi OS (_Operating System_), so it is necessary to use _raspi-config_
to enable the I2C protocol before continuing.

# 3. Dependencies

__Modbus Scale Server__ is part of the _UC-02-2024 Coffee Cart Modifications_
software suite. Scale software has been split along hardware component lines,
with the software for each hardware component residing in a separate GitLab
repository.

1. [modbus-scale-broker][modbus-scale-broker-gitlab]. The Arduino sketch that
must be downloaded to the Uno.

2. [modbus-scale-server][modbus-scale-server-gitlab]. The Modbus Ethernet
server daemon that runs on the Raspberry Pi.

3. [modbus-scale-client][modbus-scale-client-gitlab]. The Modbus Ethernet
client that queries the server.

4. [modbus-scale-ui][modbus-scale-ui-gitlab]. A [Textual][textual] UI (_User
Interface_) that displays the output of the Mazzer and Rancilio scales, and
which can be used to tare either scale.

Because the design intent is for these software repositories to be deployed
_en-masse_ as part of a comprehensive weigh scale hardware solution, various
dependencies exist between them. This must be borne in mind when deciding
whether or not to employ __Modbus Scale Server__ in isolation.

Python packages are also available for the following software components.

 - [modbus-scale-server][modbus-scale-server-pypi]
 - [modbus-scale-client][modbus-scale-client-pypi]
 - [modbus-scale-ui][modbus-scale-ui-pypi]

These packages may be installed using [pip][pip]. Note however that the caveat
regarding both hardware and software dependencies still applies.

# 4. Installation

Two installation methods are available, with the most appropriate depending on
whether the intent is to use the code base as-is, or to modify it.

## 4.1. PyPI Package

Those who wish to use the code base as-is are best served by installing the
Python [modbus-scale-server][modbus-scale-server-pypi] package via [pip][pip].

Whilst it is not strictly necessary to create a venv (_virtual environment_) in
order to deploy the package, doing so provides a Python environment that is
completely isolated from the system-wide Python install. The practical upshot
of this is that the venv can be torn-down and recreated multiple times without
issue.

    $ python -m venv ~/my_venv

Next, activate the venv and install the package. Note that once activated, the
name of the venv will be prepended to the terminal prompt.

    $ source ~/my_venv/bin/activate
    (my_venv) $ python -m pip install modbus-scale-server

## 4.2. GitLab Repository

Those who wish to modify the code base should clone the GitLab repository
instead. Again, whilst not strictly necessary to create a venv in order to
modify the code base, it is recommended to do so for the reasons stated above.

    $ python -m venv ~/my_venv
    $ source ~/my_venv/bin/activate
    (my_venv) $ cd ~/my_venv
    (my_venv) $ git clone https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024/modbus-scale-server.git

Irrespective of whether or not a venv has been created, the repository
_requirements.txt_ file may be used to ensure that the correct module
dependencies are installed.

    (my_venv) $ python -m pip install -r ~/my_venv/requirements.txt

# 5. Verification

In order to verify that __Modbus Scale Server__ has been installed correctly,
it is advisable to create a minimal working example.

    # example.py
    
    from modbus_scale_server import ModbusScaleServer

    server = ModbusScaleServer(host = "<host>", msgs = True)
    server.daemon()

After replacing `<host>` with the IPv4 (_Internet Protocol version 4_) address
of the physical host, running this example should result in output similar to
the following.

    (my_venv) $ python example.py
    [INFO] Starting daemon...
    [DATA] Scale weight = 123.4g
    [DATA] Scale weight = 123.4g
    ...
    [INFO] Stopping daemon...

Note that verification assumes that all requisite hardware and software
dependencies have been met.

# 6. Operation

No matter the chosen method of installation, it is necessary to ensure that the
Modbus Ethernet daemon is started whenever the Raspberry Pi boots. The simplest
way to achieve this is to add the following to `/etc/rc.local`.

    /home/<user>/my_venv/bin/python /home/<user>/my_venv/example.py &

All this command does is call the Python executable of the previously-created
venv and have it run the example code that starts the daemon as a background
process. Note that the full path is used in both instances as `rc.local` is run
as root, and consequently `~` is unable to be used to refer to the user's home
directory.

The final step before rebooting is to make `rc.local` executable.

    $ sudo chmod +x /etc/rc.local

# 7. Further Information 

For an overview of the entire _Coffee Cart Modifications_ project, please refer
to the GitLab [UC-02-2024][uc-02-2024-gitlab] README.

# 8. Documentation

Code has been documented using [Doxygen][doxygen].

# 9. License

__Modbus Scale Server__ is released under the [GNU General Public License][gpl].

# 10. Authors

Code by Rodney Elliott, <rodney.elliott@canterbury.ac.nz>

[uc-02-2024-gitlab]: https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024
[raspberry-pi-4-model-b]: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
[arduino-uno]: https://store.arduino.cc/products/arduino-uno-rev3-smd
[modbus-scale-broker-gitlab]: https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024/modbus-scale-broker
[modbus-scale-server-gitlab]: https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024/modbus-scale-server
[modbus-scale-client-gitlab]: https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024/modbus-scale-client
[modbus-scale-ui-gitlab]: https://gitlab.com/uc-mech-wing/robotics-control-lab/uc-02-2024/modbus-scale-ui
[modbus-scale-server-pypi]: https://pypi.org/project/modbus-scale-server/
[modbus-scale-client-pypi]: https://pypi.org/project/modbus-scale-client/
[modbus-scale-ui-pypi]: https://pypi.org/project/modbus-scale-ui/
[textual]: https://textual.textualize.io/
[pip]: https://pypi.org/project/pip/
[doxygen]: https://www.doxygen.nl
[gpl]: https://www.gnu.org/licenses/gpl-3.0.html
