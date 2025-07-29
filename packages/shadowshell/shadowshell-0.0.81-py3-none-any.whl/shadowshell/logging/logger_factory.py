#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LoggerFactory
@author: shadow shell
"""

from shadowshell.logging.console_logger import ConsoleLogger

class LoggerFactory:
        
    __logger = ConsoleLogger()

    def __init__(self):
        pass

    @staticmethod
    def get_logger(name = "default"):
        return LoggerFactory.__logger

if __name__ == "__main__":
    LoggerFactory().get_logger().info("test")
    
