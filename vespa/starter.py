#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Module name: starter.py
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
Starter
"""
import sys
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from model import Model
from view import View
from controller import Controller
from log_pipe import *

if __name__ == "__main__":
    debug5("Configuring model")
    model = Model()
    debug5("Configuring view")
    view = View(model)
    debug5("Configuring controller")
    controller = Controller(model, view)

    debug5("Starting controller")
    controller.start()
