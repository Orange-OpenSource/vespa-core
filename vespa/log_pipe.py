# -*- coding: utf-8 -*-
#
# Module name: log_pipe.py
# Version:     1.0
# Created:     29/04/2014 by Aurélien Wailly <aurelien.wailly@orange.com>
#
# Copyright (C) 2010-2014 Orange
#
# This file is part of VESPA.
#
# VESPA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation version 2.1.
#
# VESPA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with VESPA.  If not, see <http://www.gnu.org/licenses/>.

"""
log_pipe
"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def debug1(str):
    print repr(str)
    pass


def debug2(str):
    print repr(str)
    pass


def debug4(str):
    print repr(str)
    # raise Exception("Fatal!")
    raise


def debug5(str):
    print "%s[INFO]%s %s" % (bcolors.HEADER, bcolors.ENDC, str)
    pass


def debug_info(str):
    debug5(str)
    pass


def debug_comm(str):
    # print "%s[COMM]%s %s" % (bcolors.OKBLUE, bcolors.ENDC, str)
    pass


def debug_crypto(str):
    # print "%s[CRYP]%s %s" % (bcolors.OKBLUE, bcolors.ENDC, str)
    pass


def debug_comm_len(s):
    """
    Display maximum sized informations

    Notes: offloaded to prevent screen flooding
    """
    # print "%s[COMM]%s %s" % (bcolors.OKBLUE, bcolors.ENDC, s[0:200])
    # print "%s[COMM]%s %s" % (bcolors.OKBLUE, bcolors.ENDC, s)
    pass


def debug_comm_detail(str):
    """
    Display extended communications information
    - How sendRemote split RECV_LENGTH

    Notes: offloaded to prevent screen flooding
    """
    # print "%s[COMM]%s %s" % (bcolors.OKBLUE, bcolors.ENDC, str)
    pass


def debug_thread(str):
    # print "%s[THRD]%s %s" % (bcolors.FAIL, bcolors.ENDC, str)
    pass


def debug_init(str):
    # print "%s[INIT]%s %s" % (bcolors.OKGREEN, bcolors.ENDC, str)
    pass


def debug_controller(str):
    # print "%s[CNTR]%s %s" % (bcolors.OKGREEN, bcolors.ENDC, str)
    pass
