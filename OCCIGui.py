# -*- coding: utf-8 -*-
# FreeCAD tools of the OCCI workbench
# (c) 2001 Juergen Riegel
# License LGPL

import FreeCAD, FreeCADGui

class CmdSettings:
    def Activated(self):
        FreeCAD.Console.PrintMessage("Hello, World!\n")
    def IsActive(self):
        return True
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Settings', 'ToolTip': 'Settings Dialog for OCCI'}

FreeCADGui.addCommand('OCCI_Settings', CmdSettings())
