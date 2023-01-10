# -*- coding: utf-8 -*-
# OCCI gui init module

class OCCIWorkbench ( Workbench ):
    "OCCI workbench object"
    # The following line will not work correctly in some cases when running a dev setup
    # Icon = FreeCAD.getResourceDir() + "Mod/OCCI/Resources/icons/OCCIWorkbench.svg"
    Icon = FreeCAD.getUserAppDataDir() + "Mod/occi-freecad-plugin/Resources/icons/OCCIWorkbench.svg"
    MenuText = "OCCI"
    ToolTip = "OCCI workbench"

    def Initialize(self):
        # load the module
        import OCCIGui
        # self.appendToolbar('OCCI',['OCCI_HelloWorld'])
        self.appendMenu('OCCI',['OCCI_Settings'])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Activated(self):
        """
        Called when the OCCI module is selected from the workbench drop-down list.
        """
        from PySide import QtGui, QtCore

        FreeCAD.Console.PrintMessage("OCCI Module Activated")

        # A handle to the main window will allow us to configure the GUI
        main_win = FreeCADGui.getMainWindow()

        # Add the right-hand dock area for OCCI to operate
        occi_dock = QtGui.QDockWidget("Open CAD Component Interface (OCCI)")
        occi_dock.setObjectName("occi_dock")
        # occi_dock.setContentsMargins(0, 0, 0, 0)
        main_win.addDockWidget(QtCore.Qt.RightDockWidgetArea, occi_dock)

        # Populate the OCCI dock with all of the required controls
        self.PopulateOCCIDock(occi_dock)

    def Deactivated(self):
        """
        Called when another module other than OCCI is selected in the workbench drop-down list.
        """
        from PySide import QtGui, QtCore

        # A handle to the main window will allow us to configure the GUI
        main_win = FreeCADGui.getMainWindow()

        # Walk through the dock widgets to find the right sidebar
        dockWidgets = main_win.findChildren(QtGui.QDockWidget)
        for widget in dockWidgets:
            if widget.objectName() == "occi_dock":
                widget.setVisible(True)
                main_win.removeDockWidget(widget)

    def PopulateOCCIDock(self, occi_dock):
        """
        Does the heavy lifting of populating the OCCI right side dock
        with controls.
        """
        from PySide import QtGui, QtCore
        from CollapsibleWidget import CollapsibleWidget

        # We can only add widgets to a dock, so we need a top-level widget
        container = QtGui.QWidget()
        container.setStyleSheet("background-color:white;")

        # Set the top level layout of the OCCI sidebar
        vbox = QtGui.QVBoxLayout()
        # vbox.setSpacing(0)
        vbox.setAlignment(QtCore.Qt.AlignTop)

        # Introduction label widget
        intro_lbl = QtGui.QLabel()
        intro_lbl.setAlignment(QtCore.Qt.AlignLeft)
        intro_lbl.setTextFormat(QtCore.Qt.RichText)
        intro_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        intro_lbl.setOpenExternalLinks(True)
        intro_lbl.setText('Parametric CAD components for all. <a href="https://github.com/occi-cad/docs/blob/main/README.md">About</a>')
        vbox.addWidget(intro_lbl)

        # Main Repositories widget
        repos_widget = CollapsibleWidget(title="Repositories", parent=container)

        # Informational labels in Repositories widget
        repos_1_lbl = QtGui.QLabel()
        repos_1_lbl.setAlignment(QtCore.Qt.AlignCenter)
        repos_1_lbl.setTextFormat(QtCore.Qt.RichText)
        repos_1_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        repos_1_lbl.setOpenExternalLinks(True)
        repos_1_lbl.setText('We gather tested OCCI libraries at <a href="https://github.com/occi-cad/scriptlibrary">github.com/occi-cad</a>')
        repos_widget.add_widget(repos_1_lbl)
        repos_2_lbl = QtGui.QLabel()
        repos_2_lbl.setAlignment(QtCore.Qt.AlignCenter)
        repos_2_lbl.setText("You can also add others manually")
        repos_widget.add_widget(repos_2_lbl)

        # The table holding the list of repositories
        repos_tbl = QtGui.QTableWidget(4, 4)
        repos_tbl.setStyleSheet("border:none;")
        repos_tbl.setMaximumHeight(175)
        repos_tbl.setHorizontalHeaderLabels(['use', 'name', 'curated by', 'remove'])
        repos_tbl.verticalHeader().setVisible(False)
        repos_tbl.resizeColumnToContents(0)
        repos_tbl.resizeColumnToContents(1)
        repos_tbl.resizeColumnToContents(2)
        repos_tbl.resizeColumnToContents(3)

        # Load the default repositories into the table
        row = 0
        self.default_settings = self.LoadDefaults()
        for repo in self.default_settings['repositories']:
            # Set the 'use' checkbox for the repo
            cur_checkbox = QtGui.QCheckBox()
            cur_checkbox.setChecked(True)
            repos_tbl.setCellWidget(row, 0, cur_checkbox)

            # Set the name text label for the repo
            cur_name_txt = QtGui.QLabel(text=repo['name'])
            repos_tbl.setCellWidget(row, 1, cur_name_txt)

            # Set the host URL label for the repo
            cur_host_txt = QtGui.QLabel()
            cur_host_txt.setAlignment(QtCore.Qt.AlignCenter)
            cur_host_txt.setTextFormat(QtCore.Qt.RichText)
            cur_host_txt.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            cur_host_txt.setOpenExternalLinks(True)
            cur_host_txt.setText('<a href="' + repo['host_url'] + '">Archiyou</a>')
            repos_tbl.setCellWidget(row, 2, cur_host_txt)

            # Add the remove button for this repository
            cur_remove_btn = QtGui.QPushButton()
            cur_remove_btn.setFlat(True)
            cur_remove_btn.setIcon(QtGui.QIcon(':/icons/delete.svg'))
            repos_tbl.setCellWidget(row, 3, cur_remove_btn)

            row += 1

        ## Make sure all the columns are the correct size
        repos_tbl.resizeColumnToContents(0)
        repos_tbl.resizeColumnToContents(1)
        repos_tbl.resizeColumnToContents(2)
        repos_tbl.resizeColumnToContents(3)

        # Add the finished table to the collapsible widget
        repos_widget.add_widget(repos_tbl)


        # Controls for adding a new library
        add_layout = QtGui.QHBoxLayout()
        add_txt = QtGui.QLineEdit()
        add_layout.addWidget(add_txt)
        add_btn = QtGui.QPushButton(text="Add Respository")
        add_layout.addWidget(add_btn)
        repos_widget.add_layout(add_layout)

        # Add the Repositories widget to the main
        vbox.addWidget(repos_widget)

        # Set the layout for the dock with all the UI controls added to it
        container.setLayout(vbox)
        occi_dock.setWidget(container)
        occi_dock.update()


    def LoadDefaults(self):
        import yaml

        # Default settings file is YAML and is on disk
        defaults_file = FreeCAD.getUserAppDataDir() + "Mod/occi-freecad-plugin/defaults.yaml"

        # Open and parse the defaults file
        with open(defaults_file, 'r') as file:
            default_settings = yaml.safe_load(file)

        return default_settings

Gui.addWorkbench(OCCIWorkbench())
