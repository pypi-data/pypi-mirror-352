#*****************************************************************************
#
#   Module:         modbus_scale_server.py
#   Project:        UC-02-2024 Coffee Cart Modifications
#
#   Repository:     modbus-scale-server
#   Target:         Raspberry Pi
#
#   Author:         Rodney Elliott
#   Date:           28 May 2025
#
#   Description:    Contains the weigh scale Modbus Ethernet server daemon.
#
#*****************************************************************************
#
#   Copyright:      (C) 2025 Rodney Elliott
#
#   This file is part of Coffee Cart Modifications.
#
#   Coffee Cart Modifications is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the license, or (at your
#   option) any later version.
#
#   Coffee Cart Modifications is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#   Public License for more details.
#
#   You should of received a copy of the GNU General Public License along with
#   Coffee Cart Modifications. If not, see <https://www.gnu.org/licenses/>.
#
#*****************************************************************************

#*****************************************************************************
#   Doxygen file documentation
#*****************************************************************************

##
#   @file modbus_scale_server.py
#
#   @brief Contains the weigh scale Modbus Ethernet server daemon.
#
#   __Modbus Scale Server__ provides the server-side capabilities required by
#   the Mazzer and Rancilio weigh scales of project UC-02-2024 _Coffee Cart
#   Modifications_.
#
#   A Raspberry Pi 4 Model B hosts the Modbus Ethernet server daemon that
#   Modbus clients may query to obtain the current scale weight (grams), or
#   tare (zero) the scale. The daemon updates the scale weight at a frequency
#   of 10Hz.
#
#   The daemon uses non-privileged port 2593, which is unofficially assigned to
#   Ultima Online servers. This port has been chosen as use of official Modbus
#   port 502 would require elevated user privileges.

#*****************************************************************************
#   Modules
#*****************************************************************************

##
#   @package sys
#
#   The _sys_ module contains system-specific parameters and functions.
import sys

##
#   @package smbus 
#
#   The _smbus_ module contains functions to communicate using the I2C bus of
#   the Raspberry Pi.
from smbus import SMBus 

##
#   @package pyModbusTCP
#
#   The _pyModbusTCP_ module contains classes that may be used to create,
#   configure, and control Modbus Ethernet clients and servers.
from pyModbusTCP.server import ModbusServer, DataHandler, DataBank

##
#   @package time
#
#   The _time_ module provides various time-related functions.
import time

#*****************************************************************************
#   Constants
#*****************************************************************************

## ID of the Raspberry Pi I2C bus.
I2C_BUS_ID = 1

## I2C address of the (Arduino Uno) target.
I2C_ADDRESS_TARGET = 0x0b

#*****************************************************************************
#   Class
#*****************************************************************************

## The Modbus scale server class.
class ModbusScaleServer:
    ##
    #   @brief Class constructor.
    #   @param[in] host IPv4 address of the Modbus Ethernet server host.
    #   @param[in] msgs display messages (@b False (default), @b True).
    #
    #   Perform initial configuration of the Modbus Ethernet server.
    def __init__(self, host, msgs = False):
        ## IPv4 address of the Modbus Ethernet server host.
        self.host = host
        ## Display messages.
        self.msgs = msgs
        ## 
        #   @brief Previous coil state.
        #
        #   Requests from Modbus Ethernet clients to tare the scales takes
        #   the form of a rising edge on coil zero. In order to detect such
        #   edges, the current state of the coil is compared to its previous
        #   state.
        self.tare_on_rising_edge = False

        ## Instance of the SMBus object.
        self.i2c_bus = SMBus(I2C_BUS_ID)

        ## Instance of the _pyModbusTCP_ module server class.
        self.server = ModbusServer(self.host, port = 2593 , no_block = True)
        self.server.start()

    ##
    #   @brief Modbus Ethernet server daemon.
    #
    #   The Modbus Ethernet server daemon polls the Arduino Uno and stores the
    #   most recent weight value in a set of three Modbus input registers. The
    #   daemon also responds to requests from Modbus clients to tare (that is,
    #   zero) the scale. Note that as a result, negative weight values may be
    #   returned.
    def daemon(self):
        if self.msgs:
            print("[INFO] Starting daemon...")
        
        while True:
            try:
                ##
                #   Because Modbus input registers are 16-bit, it is necessary
                #   to mangle the double-precision floating-point scale values
                #   prior to storage. This is done by rounding the float to one
                #   decimal place before converting it to a string. The string
                #   is then checked for the presence of a leading negative
                #   sign, and if detected, the _modbus_sign_ input register is
                #   set to one, otherwise it is set to zero. The string, now
                #   stripped of any leading sign, is split at the decimal point
                #   and the whole number and fractional portions are converted
                #   to 16-bit integers and stored in the _modbus_full_ and
                #   _modbus_part_ input registers respectively.
                try:
                    value_rounded = self.i2c_bus.read_i2c_block_data(I2C_ADDRESS_TARGET,0x00, 8)
                    value_string = ''.join(map(chr, value_rounded))
                    value_string = value_string.lstrip()

                    if self.msgs:
                        print("[DATA] Scale weight = %sg" % value_string)

                except:
                    print("[WARN] I2C read error!")
                    value_string = "-9999.9"

                if value_string[0] == "-":
                    value_string = value_string[1:]
                    modbus_sign = 1
                else:
                    modbus_sign = 0

                value_partitioned = value_string.partition(".")
                value_full = int(value_partitioned[0])
                value_part = int(value_partitioned[2])

                modbus_full = value_full % 2**16
                modbus_part = value_part % 2**16

                self.server.data_bank.set_input_registers(0, [modbus_sign])
                self.server.data_bank.set_input_registers(1, [modbus_full])
                self.server.data_bank.set_input_registers(2, [modbus_part])

                coil = self.server.data_bank.get_coils(0)

                if not self.tare_on_rising_edge and coil[0]:
                    if self.msgs:
                        print("[INFO] Tare request received...")
                    
                    self.i2c_bus.write_byte(I2C_ADDRESS_TARGET, ord('t'))
 
                self.tare_on_rising_ege = coil[0]

                time.sleep(0.1)

            except (KeyboardInterrupt, SystemExit):
                if self.msgs:
                    print("[INFO] Stopping daemon...")
                
                sys.exit()

