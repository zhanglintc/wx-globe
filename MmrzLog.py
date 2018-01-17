#!/usr/bin/env python
# -*- coding: utf-8 -*-#

import os, sys, time
import inspect

INFO  = "I"
DEBUG = "D"
ERROR = "E"
WARN  = "W"

class MmrzLog:
    log = None

    def __init__(self):
        self.abspath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.log_path = self.abspath + "/Mmrz-Sync.log"
        self.logger = open(self.log_path, "ab")

    def __del__(self):
        self.logger.close()

    def __new__():
        if MmrzLog.log is None:
            MmrzLog.log = MmrzLog()
        else:
            return MmrzLog.log

    def _get_caller_info(self):
        file_name = inspect.currentframe().f_back.f_back.f_code.co_filename
        func_name = inspect.currentframe().f_back.f_back.f_code.co_name

        return file_name, func_name

    def _output(self, level, msg, file_name, func_name):
        today = time.strftime("%Y%m%d", time.localtime())
        mtime = time.strftime('%H:%M:%S',time.localtime())
        self.logger.write("{0} {1} {2} {3} from {4}() at {5}\n".format(today, mtime, level, msg, func_name, file_name))
        self.logger.flush()

    def i(self, msg):
        file_name, func_name = self._get_caller_info()
        self._output(INFO, msg, file_name, func_name)

    def d(self, msg):
        file_name, func_name = self._get_caller_info()
        self._output(DEBUG, msg, file_name, func_name)

    def e(self, msg):
        file_name, func_name = self._get_caller_info()
        self._output(ERROR, msg, file_name, func_name)

    def w(self, msg):
        file_name, func_name = self._get_caller_info()
        self._output(WARN, msg, file_name, func_name)

log = MmrzLog()

