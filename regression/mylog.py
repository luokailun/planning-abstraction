#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-04 00:48:22
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$

import os
import logging.config
import logging
import json


def setup_logging(
    default_path='logging.json', 
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration
 
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def getLogger(name):
    setup_logging()
    return logging.getLogger(name)


