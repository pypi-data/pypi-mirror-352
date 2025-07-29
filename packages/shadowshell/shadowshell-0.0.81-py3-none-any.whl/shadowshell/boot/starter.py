#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from shadowshell.logging import LoggingConstants, LoggerFactory
from shadowshell.config import Configurator
from shadowshell.monitor import function_monitor, performance_monitor

class_mame = "Starter"

class Starter:
    
    @function_monitor(class_mame)
    def __init__(self):
        """ 初始化"""
        # 日志
        LoggingConstants.LEVEL_INFO = True
        self.logger = LoggerFactory.get_logger()
        # 配置
        config_file_path = self.get_config_file_path()
        if config_file_path is not None: 
            self.configurator = Configurator(config_file_path)

    @function_monitor(class_mame)
    def get_config_file_path(self):
        """ 获取配置文件路径"""
        return None