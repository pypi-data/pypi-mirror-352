#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

from shadowshell.logging import LoggerFactory

class FileUtil:

    __logger = LoggerFactory.get_logger()

    @staticmethod
    def get_all(file_path, mode="r", encoding="utf-8"):
        with open(file_path, mode, encoding = encoding) as f:
                content = f.read()
        FileUtil.__logger.debug(f"[{file_path}][All content]{content}")
        return content