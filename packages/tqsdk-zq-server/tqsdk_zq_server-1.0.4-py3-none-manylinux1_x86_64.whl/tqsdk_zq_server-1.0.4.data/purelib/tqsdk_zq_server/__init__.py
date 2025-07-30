#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chenli'

from pathlib import Path


def get_zq_server_path():
    return Path(__file__, "../zq_server").resolve()
