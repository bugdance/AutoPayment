#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Gunicorn.

written by pyLeo.
"""
# # # linux使用，独角兽配置不要和程序配置相混。
from gevent import monkey
monkey.patch_all()
# # # Import current path.
import sys
sys.path.append('..')
# # # 具体参数。
bind = '0.0.0.0:18082'
debug = False
workers = 1
threads = 500
worker_class = 'gevent'
backlog = 2048
proc_name = 'gunicorn.proc'
