#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serializer

@author: shadowshell
"""

import json
from shadowshell.logging import LoggerFactory
from shadowshell.serialize.serializer import Serializer

class SerializerJson(Serializer):

    def __init__(self):
        self.logger = LoggerFactory().get_logger()
        pass
 
    def serialize(self, object):
        json_str = json.dumps(object)
        self.logger.debug(f"Serialized json string: {json_str}.")
        return json_str

    def deserialize(self, content):
        object=json.loads(content)
        return object

