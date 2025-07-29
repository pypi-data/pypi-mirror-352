#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LoggerFactory
@author: shadowshell
"""

from shadowshell.logging import LoggerFactory

class Test():

    def test(self):
        LoggerFactory().get_logger().info("jhaohao")