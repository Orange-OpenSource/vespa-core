# -*- coding: utf-8 -*-
#
# Module name: supervisor.py
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

import wx
from .SupervisorMainFrame import SupervisorMainFrame

if __name__ == '__main__':
    app = wx.App(redirect=True, filename="logwx.txt")
    top = SupervisorMainFrame(None)
    top.Show()
    app.MainLoop()

# http://orange-business.com/fr/entreprise/thematiques/cloud/animation/
