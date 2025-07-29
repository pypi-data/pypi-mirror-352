#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configurator
@author: shadowshell
"""

import configparser

from shadowshell.monitor import function_monitor

class_name = "Configurator"

class Configurator:

    config = None;

    @function_monitor(class_name)
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
    @function_monitor(class_name)
    def get(self, group, key):
        value = self.config.get(group, key)
        return value


