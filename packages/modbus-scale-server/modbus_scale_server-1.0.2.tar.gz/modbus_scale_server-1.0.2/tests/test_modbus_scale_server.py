#*****************************************************************************
#
#   Module:         test_modbus_scale_server.py
#   Project:        UC-02-2024 Coffee Cart Modifications
#
#   Repository:     modbus-scale-server
#   Target:         Raspberry Pi
#
#   Author:         Rodney Elliott
#   Date:           3 June 2025
#
#   Description:    Contains the weigh scale Modbus Ethernet server daemon test
#                   suite.
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
#   @file test_modbus_scale_server.py
#
#   @brief Contains the weigh scale Modbus Ethernet server daemon test suite.
#
#   Due to the fact that __Modbus Scale Server__ has a number of physical
#   hardware dependencies, this suite is currently devoid of actual tests.

#*****************************************************************************
#   Modules
#*****************************************************************************

##
#   @package modbus_scale_server
#
#   The _modbus_scale_server_ module contains the weigh scale Modbus Ethernet
#   server daemon.
from modbus_scale_server import ModbusScaleServer

#*****************************************************************************
#   Tests
#*****************************************************************************

##
#   @brief Test zero.
#
#   This is required for the GitLab CI/CD pipeline to pass the test stage. 
def test_0():
    pass

