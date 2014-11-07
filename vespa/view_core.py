# -*- coding: utf-8 -*-
#
# Module name: view_core.py
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

###########################################################################
# Python code generated with wxFormBuilder (version Sep  8 2010)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.grid
import wx.richtext

###########################################################################
# Class MainFrame
###########################################################################


class MainFrame (wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=u"Supervisor",
            pos=wx.DefaultPosition,
            size=wx.Size(
                967,
                740),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        self.MainMenu = wx.MenuBar(0)
        self.menuFicher = wx.Menu()
        self.m_menuItem1 = wx.MenuItem(
            self.menuFicher,
            wx.ID_ANY,
            u"Ouvrir Archi",
            wx.EmptyString,
            wx.ITEM_NORMAL)
        self.menuFicher.AppendItem(self.m_menuItem1)

        self.m_menuItem2 = wx.MenuItem(
            self.menuFicher,
            wx.ID_ANY,
            u"Fermer Archi",
            wx.EmptyString,
            wx.ITEM_NORMAL)
        self.menuFicher.AppendItem(self.m_menuItem2)

        self.menuFicher.AppendSeparator()

        self.m_menuItem3 = wx.MenuItem(
            self.menuFicher,
            wx.ID_ANY,
            u"Quitter",
            wx.EmptyString,
            wx.ITEM_NORMAL)
        self.menuFicher.AppendItem(self.m_menuItem3)

        self.MainMenu.Append(self.menuFicher, u"Fichier")

        self.menuEdition = wx.Menu()
        self.MainMenu.Append(self.menuEdition, u"Edition")

        self.menuBoucles = wx.Menu()
        self.MainMenu.Append(self.menuBoucles, u"Boucles")

        self.SetMenuBar(self.MainMenu)

        self.MainStatusBar = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)
        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        gbSizer2 = wx.GridBagSizer(0, 0)
        gbSizer2.AddGrowableCol(1)
        gbSizer2.AddGrowableRow(0)
        gbSizer2.SetFlexibleDirection(wx.BOTH)
        gbSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.archiTree = wx.TreeCtrl(
            self, wx.ID_ANY, wx.DefaultPosition, wx.Size(
                200, -1), wx.TR_DEFAULT_STYLE)
        gbSizer2.Add(
            self.archiTree, wx.GBPosition(
                0, 0), wx.GBSpan(
                1, 1), wx.EXPAND, 5)

        self.m_notebook1 = wx.Notebook(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            0)
        self.InfoPanel = wx.Panel(
            self.m_notebook1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL)
        bSizer7 = wx.BoxSizer(wx.VERTICAL)

        self.InfoGrid = wx.grid.Grid(
            self.InfoPanel,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.HSCROLL | wx.VSCROLL)

        # Grid
        self.InfoGrid.CreateGrid(0, 0)
        self.InfoGrid.EnableEditing(False)
        self.InfoGrid.EnableGridLines(True)
        self.InfoGrid.EnableDragGridSize(False)
        self.InfoGrid.SetMargins(0, 0)

        # Columns
        self.InfoGrid.EnableDragColMove(False)
        self.InfoGrid.EnableDragColSize(True)
        self.InfoGrid.SetColLabelSize(30)
        self.InfoGrid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.InfoGrid.AutoSizeRows()
        self.InfoGrid.EnableDragRowSize(True)
        self.InfoGrid.SetRowLabelSize(80)
        self.InfoGrid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.InfoGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.InfoGrid.SetMinSize(wx.Size(-1, 2))

        bSizer7.Add(self.InfoGrid, 1, wx.EXPAND, 5)

        self.InfoPanel.SetSizer(bSizer7)
        self.InfoPanel.Layout()
        bSizer7.Fit(self.InfoPanel)
        self.m_notebook1.AddPage(self.InfoPanel, u"Informations", True)
        self.GlobalViewPanel = wx.Panel(
            self.m_notebook1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL)
        #self.m_notebook1.AddPage( self.GlobalViewPanel, u"Vue globale", False )

        gbSizer2.Add(
            self.m_notebook1, wx.GBPosition(
                0, 1), wx.GBSpan(
                1, 1), wx.EXPAND, 5)

        bSizer5.Add(gbSizer2, 1, wx.EXPAND, 5)

        self.richTextConsole = wx.richtext.RichTextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(
                -1,
                200),
            0 | wx.VSCROLL | wx.WANTS_CHARS)
        bSizer5.Add(self.richTextConsole, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer5)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onClose, id=self.m_menuItem3.GetId())
        self.archiTree.Bind(
            wx.EVT_TREE_ITEM_RIGHT_CLICK,
            self.drawTreeItemMenu)
        self.archiTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.updateTreeSelection)
        self.GlobalViewPanel.Bind(wx.EVT_PAINT, self.on_paint)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onClose(self, event):
        event.Skip()

    def drawTreeItemMenu(self, event):
        event.Skip()

    def updateTreeSelection(self, event):
        event.Skip()

    def on_paint(self, event):
        event.Skip()
