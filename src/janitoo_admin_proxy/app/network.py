# -*- coding: utf-8 -*-
"""The Node

about the pollinh mechanism :
 - simplest way to do it : define a poll_thread_timer for every value that needed to publish its data
 - Add a kind of polling queue that will launch the method to get and publish the value

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+                                   # pragma: no cover
    from logging import NullHandler                   # pragma: no cover
except ImportError:                                   # pragma: no cover
    class NullHandler(logging.Handler):               # pragma: no cover
        """NullHandler logger for python 2.6"""       # pragma: no cover
        def emit(self, record):                       # pragma: no cover
            pass                                      # pragma: no cover
logger = logging.getLogger( __name__ )
import threading
import datetime
from flask import request
from janitoo.value import JNTValue
from janitoo.node import JNTNode
from janitoo.utils import HADD, HADD_SEP, json_dumps, json_loads, hadd_split
from janitoo.dhcp import HeartbeatMessage, check_heartbeats, CacheManager, JNTNetwork
from janitoo.mqtt import MQTTClient
from janitoo.options import JNTOptions

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_WEB_CONTROLLER = 0x1030
COMMAND_WEB_RESOURCE = 0x1031

assert(COMMAND_DESC[COMMAND_WEB_CONTROLLER] == 'COMMAND_WEB_CONTROLLER')
assert(COMMAND_DESC[COMMAND_WEB_RESOURCE] == 'COMMAND_WEB_RESOURCE')
##############################################################

def extend( self ):

    def find_webcontrollers():
        """Return a dict with the web controller
        """
        res = {}
        web_servers = [node for node in self.nodes if COMMAND_WEB_CONTROLLER in self.nodes[node]['cmd_classes']]
        for node in  web_servers :
            if node in self.basics:
                res[node] = {}
                for value in self.basics[node]:
                    res[node][value] = {}
                    for index in self.basics[node][value]:
                        if self.basics[node][value][index]['cmd_class'] == COMMAND_WEB_CONTROLLER:
                            res[node][value][index] = {
                                'value_uuid':self.basics[node][value][index]['uuid'],
                                'value_index':self.basics[node][value][index]['index'],
                                'data':self.basics[node][value][index]['data'],
                                'label':self.basics[node][value][index]['label'],
                                'help':self.basics[node][value][index]['data'],
                            }
        return res
    self.find_webcontrollers = find_webcontrollers

    def find_webresources():
        """Return a dict with the web controller
        """
        res = {}
        web_resources = [node for node in self.nodes if COMMAND_WEB_RESOURCE in self.nodes[node]['cmd_classes']]
        for node in  web_resources :
            if node in self.basics:
                res[node] = {}
                for value in self.basics[node]:
                    res[node][value] = {}
                    for index in self.basics[node][value]:
                        if self.basics[node][value][index]['cmd_class'] == COMMAND_WEB_RESOURCE:
                            res[node][value][index] = {
                                'value_uuid':self.basics[node][value][index]['uuid'],
                                'value_index':self.basics[node][value][index]['index'],
                                'data':self.basics[node][value][index]['data'],
                                'label':self.basics[node][value][index]['label'],
                                'help':self.basics[node][value][index]['data'],
                            }
        return res
    self.find_webresources = find_webresources
