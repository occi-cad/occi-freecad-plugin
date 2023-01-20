# -*- coding: utf-8 -*-
# FreeCAD tools of the OCCI workbench
# (c) 2001 Juergen Riegel
# License LGPL

import FreeCAD, FreeCADGui

class CmdReset:
    def Activated(self):
        from PySide import QtGui
        from PySide.QtCore import QSettings

        # Reset the dictionary of repos in the settings
        settings = QSettings("OCCI", "occi-freecad-plugin")
        settings.setValue('data/repo_list', {'list': [{'use': True, 'library': 'OCCI test', 'maintainer': 'Mark van der Net', 'models_url': 'https://occi.archiyou.nl'}]})
        settings.sync()

        QtGui.QMessageBox.information(None, "OCCI Repository Reset", "The list of OCCI repositories has been reset. Please restart this workbench to have the changes take effect.")


    def IsActive(self):
        return True


    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Reset Repositories', 'ToolTip': 'Resets the list of repositories back to the default'}


FreeCADGui.addCommand('OCCI_Reset_Repos', CmdReset())
