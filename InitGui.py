# -*- coding: utf-8 -*-
# OCCI gui init module

class OCCIWorkbench ( Workbench ):
    "OCCI workbench object"
    # The following line will not work correctly in some cases when running a dev setup
    # Icon = FreeCAD.getResourceDir() + "Mod/OCCI/Resources/icons/OCCIWorkbench.svg"
    Icon = FreeCAD.getUserAppDataDir() + "Mod/occi-freecad-plugin/Resources/icons/OCCIWorkbench.svg"
    MenuText = "OCCI"
    ToolTip = "OCCI workbench"
    json_search_results = None  # Holds the results when a user searches for an OCCI component
    presets_layout = None  # Holds all of the preset buttons, but needs to be reset when a new component is selected
    presets_controls = []  # Keeps the preset button objects separate from each other
    presets = {}  # All of the presets that have been dynamically loaded
    use_checks = []  # Holds the check boxes for whether or not to include each repository in searches
    remove_buttons = []  # Holds the buttons to remove each of the repository entries


    def Initialize(self):
        from PySide.QtCore import QSettings

        # load the module
        import OCCIGui
        self.appendMenu('OCCI',['OCCI_Reset_Repos'])

        # Check to see if this is the first time the plugin has run
        settings = QSettings("OCCI", "occi-freecad-plugin")
        is_first_run = settings.value('misc/is_first_run')

        # If this is the first run, set some defaults
        if is_first_run == None:
            # Make sure we do not enter this section again
            settings.setValue('misc/is_first_run', False)

            # Give sane defaults for all the settings
            settings.setValue('ui/repos_expanded', 'yes')
            settings.setValue('ui/comps_expanded', 'yes')
            settings.setValue('ui/params_expanded', 'yes')
            settings.setValue('ui/auto_update', 'no')
            settings.setValue('data/repo_list', {'list': [{'use': True, 'library': 'OCCI test', 'maintainer': 'Mark van der Net', 'models_url': 'https://occi.archiyou.nl'}]})

            # Write all the settings to disk
            settings.sync()


    def GetClassName(self):
        return "Gui::PythonWorkbench"


    def Activated(self):
        """
        Called when the OCCI module is selected from the workbench drop-down list.
        """
        from PySide import QtGui, QtCore

        FreeCAD.Console.PrintMessage("OCCI Module Activated\r\n")

        # A handle to the main window will allow us to configure the GUI
        main_win = FreeCADGui.getMainWindow()

        # Add the right-hand dock area for OCCI to operate
        occi_dock = QtGui.QDockWidget("Open CAD Component Interface (OCCI)")
        occi_dock.setObjectName("occi_dock")
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
        from functools import partial
        from PySide import QtGui, QtCore
        from PySide.QtCore import QSettings

        toggle_button_css = "border:none;background-color:#D8D8D8;font-size:18px;"

        # Make sure this method has access to the settings
        settings = QtCore.QSettings("OCCI", "occi-freecad-plugin")

        # Build a collapsible GUI widget
        tree_widget = QtGui.QTreeWidget()
        tree_widget.header().hide()
        tree_widget.setRootIsDecorated(False)

        # Assemble the contents of the Repositories expandable widget
        main_vbox = QtGui.QVBoxLayout()
        main_vbox.setAlignment(QtCore.Qt.AlignTop)

        # Introduction label widget
        intro_lbl = QtGui.QLabel()
        intro_lbl.setAlignment(QtCore.Qt.AlignCenter)
        intro_lbl.setTextFormat(QtCore.Qt.RichText)
        intro_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        intro_lbl.setOpenExternalLinks(True)
        intro_lbl.setStyleSheet("margin-top:10px;")
        intro_lbl.setText('Parametric CAD components for all. <a href="https://github.com/occi-cad/docs/blob/main/README.md">About</a>')
        main_vbox.addWidget(intro_lbl)

        # Documentation link
        docs_lbl = QtGui.QLabel()
        docs_lbl.setAlignment(QtCore.Qt.AlignCenter)
        docs_lbl.setTextFormat(QtCore.Qt.RichText)
        docs_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        docs_lbl.setOpenExternalLinks(True)
        docs_lbl.setStyleSheet("margin-bottom:10px;")
        docs_lbl.setText('<a href="https://github.com/occi-cad/occi-freecad-plugin/blob/main/docs/index.md">Documentation</a>')
        main_vbox.addWidget(docs_lbl)

        #####################################################################
        # Repos collapsible widget start                                    #
        #####################################################################
        # Set up the repositories controls widget
        repos_controls_widget = QtGui.QWidget()
        repos_controls_layout = QtGui.QVBoxLayout()
        repos_controls_widget.setLayout(repos_controls_layout)

        # Informational labels in Repositories widget
        repos_1_lbl = QtGui.QLabel()
        repos_1_lbl.setAlignment(QtCore.Qt.AlignCenter)
        repos_1_lbl.setTextFormat(QtCore.Qt.RichText)
        repos_1_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        repos_1_lbl.setOpenExternalLinks(True)
        repos_1_lbl.setText('We gather tested OCCI libraries at <a href="https://github.com/occi-cad/scriptlibrary">github.com/occi-cad</a>')
        repos_controls_layout.addWidget(repos_1_lbl)
        repos_2_lbl = QtGui.QLabel()
        repos_2_lbl.setAlignment(QtCore.Qt.AlignCenter)
        repos_2_lbl.setText("You can also add others manually")
        repos_controls_layout.addWidget(repos_2_lbl)

        # The table holding the list of repositories
        self.repos_tbl = QtGui.QTableWidget(4, 4)
        self.repos_tbl.setStyleSheet("border:none;")
        self.repos_tbl.setMaximumHeight(175)
        self.repos_tbl.setHorizontalHeaderLabels(['use', 'name', 'curated by', 'remove'])
        self.repos_tbl.verticalHeader().setVisible(False)
        header = self.repos_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtGui.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtGui.QHeaderView.ResizeMode.ResizeToContents)

        # Load the default repositories into the table
        row = 0
        # self.default_settings = self.LoadDefaults()
        repos = settings.value('data/repo_list')
        for repo in repos['list']:
            # Set the 'use' checkbox for the repo
            self.use_checks.append(QtGui.QCheckBox(objectName=repo['library'] + "_" + repo['maintainer']))
            self.use_checks[-1].setChecked(repo['use'])
            self.use_checks[-1].stateChanged.connect(partial(self.UseCheckboxChanged, self.use_checks[-1]))
            self.repos_tbl.setCellWidget(row, 0, self.use_checks[-1])

            # Set the name text label for the repo
            cur_name_txt = QtGui.QLabel()
            cur_name_txt.setAlignment(QtCore.Qt.AlignCenter)
            cur_name_txt.setTextFormat(QtCore.Qt.RichText)
            cur_name_txt.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            cur_name_txt.setOpenExternalLinks(True)
            cur_name_txt.setText('<a href="' + repo['models_url'] + '">' + repo['library'] + '</a>')
            self.repos_tbl.setCellWidget(row, 1, cur_name_txt)

            # Set the host URL label for the repo
            cur_host_txt = QtGui.QLabel()
            cur_host_txt.setAlignment(QtCore.Qt.AlignCenter)
            # cur_host_txt.setTextFormat(QtCore.Qt.RichText)
            # cur_host_txt.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            # cur_host_txt.setOpenExternalLinks(True)
            # cur_host_txt.setText('<a href="' + repo['host_url'] + '">' + repo['host_name'] + '</a>')
            cur_host_txt.setText(repo['maintainer'])
            self.repos_tbl.setCellWidget(row, 2, cur_host_txt)

            # Create the remove button for this repository
            self.remove_buttons.append(QtGui.QPushButton(objectName=repo['library'] + "_" + repo['maintainer']))
            self.remove_buttons[row].setFlat(True)
            self.remove_buttons[row].setIcon(QtGui.QIcon(':/icons/delete.svg'))
            self.remove_buttons[row].clicked.connect(partial(self.RemoveRepository, self.remove_buttons[row]))
            self.repos_tbl.setCellWidget(row, 3, self.remove_buttons[row])

            row += 1

        ## Make sure all the columns are the correct size
        self.repos_tbl.resizeColumnToContents(0)
        self.repos_tbl.resizeColumnToContents(1)
        self.repos_tbl.resizeColumnToContents(2)
        self.repos_tbl.resizeColumnToContents(3)

        # Add the finished table to the collapsible widget
        repos_controls_layout.addWidget(self.repos_tbl)

        # Controls for adding a new library
        add_layout = QtGui.QHBoxLayout()
        self.add_txt = QtGui.QLineEdit()
        # self.add_txt.setStyleSheet("border: 1px solid gray;")
        self.add_txt.setPlaceholderText("New OCCI URL")
        self.add_txt.returnPressed.connect(self.AddRepository)
        add_layout.addWidget(self.add_txt)
        add_btn = QtGui.QPushButton(text="Add Respository")
        add_btn.clicked.connect(self.AddRepository)
        add_btn.setMinimumHeight(30)
        add_btn.setStyleSheet("background-color:#DDDDDD;")
        add_layout.addWidget(add_btn)
        repos_controls_layout.addLayout(add_layout)

        # Progress bar to keep users from guessing if there is work being done in the background
        self.repos_progress_bar = QtGui.QProgressBar()
        self.repos_progress_bar.setMinimum(0)
        self.repos_progress_bar.setMaximum(100)
        repos_controls_layout.addWidget(self.repos_progress_bar)

        #####################################################################
        # Repos collapsible widget end                                      #
        #####################################################################

        #####################################################################
        # Add component collapsible widget start                            #
        #####################################################################

        # Set up the add component controls widget
        comps_controls_widget = QtGui.QWidget()
        comps_controls_layout = QtGui.QVBoxLayout()
        comps_controls_widget.setLayout(comps_controls_layout)

        # Controls to search for a component
        search_layout = QtGui.QHBoxLayout()
        self.search_txt = QtGui.QLineEdit()
        self.search_txt.setPlaceholderText("Component search text")
        self.search_txt.returnPressed.connect(self.DoSearch)
        search_layout.addWidget(self.search_txt)
        search_btn = QtGui.QPushButton(text="Search")
        search_btn.clicked.connect(self.SearchComponents)
        search_layout.addWidget(search_btn)
        comps_controls_layout.addLayout(search_layout)

        # Label that tells the user how many results were returned
        self.results_num_lbl = QtGui.QLabel(text="")
        self.results_num_lbl.setAlignment(QtCore.Qt.AlignCenter)
        comps_controls_layout.addWidget(self.results_num_lbl)

        # The table that holds the searched-for components
        self.results_tbl = QtGui.QTableWidget(4, 3)
        self.results_tbl.setStyleSheet("border:none;")
        self.results_tbl.setMaximumHeight(140)
        self.results_tbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.results_tbl.clicked.connect(self.LoadParameters)
        self.results_tbl.setHorizontalHeaderLabels(['name', 'author', 'description'])
        header = self.results_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QtGui.QHeaderView.ResizeMode.Stretch)
        comps_controls_layout.addWidget(self.results_tbl)

        # Button to add and configure the component
        component_btn_layout = QtGui.QHBoxLayout()
        component_btn = QtGui.QPushButton(text="Add Component")
        component_btn.clicked.connect(self.LoadComponent)
        component_btn_layout.addStretch()
        component_btn_layout.addWidget(component_btn)
        comps_controls_layout.addLayout(component_btn_layout)

        # Progress bar to keep users from guessing if there is work being done in the background
        self.search_progress_bar = QtGui.QProgressBar()
        self.search_progress_bar.setMinimum(0)
        self.search_progress_bar.setMaximum(100)
        comps_controls_layout.addWidget(self.search_progress_bar)

        #####################################################################
        # Add component collapsible widget end                              #
        #####################################################################

        #####################################################################
        # Configuration collapsible widget start                            #
        #####################################################################

        # Set up the add component controls widget
        config_controls_widget = QtGui.QWidget()
        self.config_controls_layout = QtGui.QVBoxLayout()
        config_controls_widget.setLayout(self.config_controls_layout)

        # Add the description labels
        self.selected_comp_lbl = QtGui.QLabel(text="No component selected")
        self.selected_comp_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.config_controls_layout.addWidget(self.selected_comp_lbl)
        self.model_info_lbl = QtGui.QLabel(text="No model loaded")
        self.model_info_lbl.setStyleSheet("color:#aaaaaa;")
        self.config_controls_layout.addWidget(self.model_info_lbl)
        self.source_info_lbl = QtGui.QLabel(text="No model loaded")
        self.source_info_lbl.setStyleSheet("color:#aaaaaa;")
        self.source_info_lbl.setTextFormat(QtCore.Qt.RichText)
        self.source_info_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.source_info_lbl.setOpenExternalLinks(True)
        self.config_controls_layout.addWidget(self.source_info_lbl)

        # Label for the parameters section
        params_lbl = QtGui.QLabel(text="Parameters")
        params_lbl.setAlignment(QtCore.Qt.AlignCenter)
        params_lbl.setStyleSheet("font-size:20px;")
        self.config_controls_layout.addWidget(params_lbl)

        # Add the parameters table
        self.params_tbl = QtGui.QTableWidget(4, 3)
        # self.params_tbl.setStyleSheet("border:none;")
        self.params_tbl.setMaximumHeight(121)
        self.params_tbl.verticalHeader().setVisible(False)
        self.params_tbl.horizontalHeader().setVisible(False)
        header = self.params_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtGui.QHeaderView.ResizeMode.Stretch)
        self.config_controls_layout.addWidget(self.params_tbl)

        # Update controls
        update_layout = QtGui.QHBoxLayout()
        self.auto_update_chk = QtGui.QCheckBox(text="auto update")
        self.auto_update_chk.setChecked(settings.value('ui/auto_update') == 'yes')
        self.auto_update_chk.stateChanged.connect(self.CheckBoxChanged)
        update_layout.addWidget(self.auto_update_chk)
        update_btn = QtGui.QPushButton(text="Update Component")
        update_btn.clicked.connect(self.UpdateComponent)
        update_layout.addWidget(update_btn)
        self.config_controls_layout.addLayout(update_layout)

        # Label for the parameters section
        presets_lbl = QtGui.QLabel(text="Presets")
        presets_lbl.setAlignment(QtCore.Qt.AlignCenter)
        presets_lbl.setStyleSheet("font-size:20px;")
        self.config_controls_layout.addWidget(presets_lbl)

        # Lets the user know that no presets are loaded
        self.presets_info_lbl = QtGui.QLabel(text="No presets loaded")
        self.presets_info_lbl.setStyleSheet("color:#aaaaaa;")
        self.config_controls_layout.addWidget(self.presets_info_lbl)
        self.presets_layout = QtGui.QGridLayout()
        self.config_controls_layout.addLayout(self.presets_layout)

        #####################################################################
        # Configuration collapsible widget end                              #
        #####################################################################

        ##################################################################
        # Custom repositories collapsible area button
        self.repos_toggle_widget = QtGui.QWidget()
        self.repos_toggle_widget.setStyleSheet(toggle_button_css)
        self.repos_toggle_widget.setMaximumHeight(40)
        self.repos_toggle_layout = QtGui.QGridLayout()
        self.repos_toggle_button = QtGui.QToolButton(text="Repositories")
        self.repos_toggle_button.setStyleSheet(toggle_button_css)
        self.repos_toggle_button.clicked.connect(self.ToggleRepoWidgets)
        self.repos_toggle_layout.addWidget(self.repos_toggle_button, 0, 0, 1, 11, QtCore.Qt.AlignCenter)
        self.toggle_repos_arrow = QtGui.QToolButton(text="")
        self.toggle_repos_arrow.setStyleSheet(toggle_button_css)
        self.toggle_repos_arrow.setArrowType(QtGui.Qt.UpArrow)
        self.toggle_repos_arrow.clicked.connect(self.ToggleRepoWidgets)
        self.repos_toggle_layout.addWidget(self.toggle_repos_arrow, 0, 12, 1, 1)
        self.repos_toggle_widget.setLayout(self.repos_toggle_layout)

        # Set up the repos widget tree item
        self.repo_widget_item = QtGui.QTreeWidgetItem(["Repositories"])
        repo_controls_item = QtGui.QTreeWidgetItem(["item1"])
        self.repo_widget_item.addChild(repo_controls_item)

        # Custom components collapsible area button
        self.comps_toggle_widget = QtGui.QWidget()
        self.comps_toggle_widget.setStyleSheet(toggle_button_css)
        self.comps_toggle_widget.setMaximumHeight(40)
        self.comps_toggle_layout = QtGui.QGridLayout()
        self.comps_toggle_button = QtGui.QToolButton(text="Add Parametric Component")
        self.comps_toggle_button.setStyleSheet(toggle_button_css)
        self.comps_toggle_button.clicked.connect(self.ToggleCompsWidgets)
        self.comps_toggle_layout.addWidget(self.comps_toggle_button, 0, 0, 1, 11, QtCore.Qt.AlignCenter)
        self.toggle_comps_arrow = QtGui.QToolButton(text="")
        self.toggle_comps_arrow.setStyleSheet(toggle_button_css)
        self.toggle_comps_arrow.setArrowType(QtGui.Qt.UpArrow)
        self.toggle_comps_arrow.clicked.connect(self.ToggleRepoWidgets)
        self.comps_toggle_layout.addWidget(self.toggle_comps_arrow, 0, 12, 1, 1)
        self.comps_toggle_widget.setLayout(self.comps_toggle_layout)

        # Set up the components widget tree item
        self.comps_widget_item = QtGui.QTreeWidgetItem(["Components"])
        comps_controls_item = QtGui.QTreeWidgetItem(["item2"])
        self.comps_widget_item.addChild(comps_controls_item)
        self.comps_widget_item.setExpanded(True)

        # Custom configuration button
        self.conf_toggle_widget = QtGui.QWidget()
        self.conf_toggle_widget.setStyleSheet(toggle_button_css)
        self.conf_toggle_widget.setMaximumHeight(40)
        self.conf_toggle_layout = QtGui.QGridLayout()
        self.conf_toggle_button = QtGui.QPushButton(text="Configure Selected Component")
        self.conf_toggle_button.setStyleSheet(toggle_button_css)
        self.conf_toggle_button.clicked.connect(self.ToggleParamsWidgets)
        self.conf_toggle_layout.addWidget(self.conf_toggle_button, 0, 0, 1, 11, QtCore.Qt.AlignCenter)
        self.toggle_conf_arrow = QtGui.QToolButton(text="")
        self.toggle_conf_arrow.setStyleSheet(toggle_button_css)
        self.toggle_conf_arrow.setArrowType(QtGui.Qt.UpArrow)
        self.toggle_conf_arrow.clicked.connect(self.ToggleRepoWidgets)
        self.conf_toggle_layout.addWidget(self.toggle_conf_arrow, 0, 12, 1, 1)
        self.conf_toggle_widget.setLayout(self.conf_toggle_layout)

        # Set up the configuration widget tree item
        self.conf_widget_item = QtGui.QTreeWidgetItem(["Configuration"])
        config_controls_item = QtGui.QTreeWidgetItem(["item3"])
        self.conf_widget_item.addChild(config_controls_item)
        self.conf_widget_item.setExpanded(True)

        # Set up the tree widgets
        tree_widget.addTopLevelItems([self.repo_widget_item, self.comps_widget_item, self.conf_widget_item])
        tree_widget.setItemWidget(self.repo_widget_item, 0, self.repos_toggle_widget)
        tree_widget.setItemWidget(self.comps_widget_item, 0, self.comps_toggle_widget)
        tree_widget.setItemWidget(self.conf_widget_item, 0, self.conf_toggle_widget)
        tree_widget.setItemWidget(repo_controls_item, 0, repos_controls_widget)
        tree_widget.setItemWidget(comps_controls_item, 0, comps_controls_widget)
        tree_widget.setItemWidget(config_controls_item, 0, config_controls_widget)

        # Expand the top level tree widgets as appropriate
        self.repo_widget_item.setExpanded(settings.value('ui/repos_expanded') == 'yes')
        self.comps_widget_item.setExpanded(settings.value('ui/comps_expanded') == 'yes')
        self.conf_widget_item.setExpanded(settings.value('ui/params_expanded') == 'yes')

        # Make sure all the toggle icons start out in the right state
        self.UpdateTreeToggleIcons()

        # Add our collapsible tree GUI arrangement to the dock
        main_vbox.addWidget(tree_widget)

        # We can only add widgets to a dock, so we need a top-level widget
        container = QtGui.QWidget()
        container.setStyleSheet("background-color:white;")

        # Set the layout for the dock with all the UI controls added to it
        main_vbox.setMargin(0)
        container.setLayout(main_vbox)
        scroll_area = QtGui.QScrollArea()
        tree_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        container.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        scroll_area.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        occi_dock.setMinimumWidth(350)
        occi_dock.setWidget(scroll_area)


    def UpdateTreeToggleIcons(self):
        """
        The toggle indicators on this UI are custom, so they have to be handled manually.
        """
        from PySide import QtGui

        # The repos indicator
        if self.repo_widget_item.isExpanded() == True:
            self.toggle_repos_arrow.setArrowType(QtGui.Qt.DownArrow)
        else:
            self.toggle_repos_arrow.setArrowType(QtGui.Qt.RightArrow)

        # The components indicator
        if self.comps_widget_item.isExpanded() == True:
            self.toggle_comps_arrow.setArrowType(QtGui.Qt.DownArrow)
        else:
            self.toggle_comps_arrow.setArrowType(QtGui.Qt.RightArrow)

        # The parameters indicator
        if self.conf_widget_item.isExpanded() == True:
            self.toggle_conf_arrow.setArrowType(QtGui.Qt.DownArrow)
        else:
            self.toggle_conf_arrow.setArrowType(QtGui.Qt.RightArrow)


    def ToggleRepoWidgets(self):
        """
        Used to toggle the repo widgets.
        """
        from PySide import QtGui
        from PySide.QtCore import QSettings

        # Save the new state as a setting
        settings = QSettings("OCCI", "occi-freecad-plugin")
        settings.setValue("ui/repos_expanded", 'yes' if not self.repo_widget_item.isExpanded() else 'no')
        settings.sync()

        # Set the expanded state
        self.repo_widget_item.setExpanded(not self.repo_widget_item.isExpanded())

        # Update the indicator arrow
        self.UpdateTreeToggleIcons()


    def ToggleCompsWidgets(self):
        """
        Used to toggle the components widgets.
        """
        from PySide.QtCore import QSettings

        # Save the new state as a setting
        settings = QSettings("OCCI", "occi-freecad-plugin")
        settings.setValue("ui/comps_expanded", 'yes' if not self.comps_widget_item.isExpanded() else 'no')
        settings.sync()

        # Set the collapsed state of the tree item
        self.comps_widget_item.setExpanded(not self.comps_widget_item.isExpanded())

        # Update the indicator arrow
        self.UpdateTreeToggleIcons()


    def ToggleParamsWidgets(self):
        """
        Used to toggle the configuration widgets.
        """
        from PySide.QtCore import QSettings

        # Save the new state as a setting
        settings = QSettings("OCCI", "occi-freecad-plugin")
        settings.setValue("ui/params_expanded", 'yes' if not self.conf_widget_item.isExpanded() else 'no')
        settings.sync()

        # Set the collapsed state of the tree item
        self.conf_widget_item.setExpanded(not self.conf_widget_item.isExpanded())

        # Update the indicator arrow
        self.UpdateTreeToggleIcons()


    def AddRepository(self):
        """
        Loads the data for the given repository and adds it to the table.
        """
        from functools import partial
        import requests
        import json
        from PySide import QtGui, QtCore

        # Get the repository URL entered by the user
        repo_url = self.add_txt.text()

        # Let the user know about common errors
        if repo_url == "":
            FreeCAD.Console.PrintWarning("OCCI: Please enter a Repository URL.\r\n")
            return
        elif not repo_url.startswith("https://"):
            FreeCAD.Console.PrintWarning("OCCI: Only https repositories are supported.\r\n")
            return

        # Let the user know that something is going on
        self.repos_progress_bar.setTextVisible(True)
        self.repos_progress_bar.setValue(20)
        QtCore.QCoreApplication.processEvents()

        # Attempt to load the URL
        response = None
        try:
            response = requests.get(repo_url)
        except:
            FreeCAD.Console.PrintError("OCCI ERROR: There was a problem loading the URL. Please verify that the URL is valid.\r\n")

        # If there was no response, there is no reason to continue
        if response == None:
            # Make sure that the progress bar does not hang
            self.repos_progress_bar.setTextVisible(False)
            self.repos_progress_bar.setValue(0)
            QtCore.QCoreApplication.processEvents()
            return

        # Let the user know there has been progress
        self.repos_progress_bar.setValue(70)
        QtCore.QCoreApplication.processEvents()

        # Check the status code to see if the request succeeded
        if response.status_code == 200:
            # Attempt to parse the response into JSON
            try:
                server_info = json.loads(response.content)
            except:
                FreeCAD.Console.PrintError("OCCI ERROR: There was an error parsing the JSON content. Please ensure that the provided URL points to a valid OCCI server.\r\n")

                # Make sure that the progress bar does not hang
                self.repos_progress_bar.setTextVisible(False)
                self.repos_progress_bar.setValue(0)
                QtCore.QCoreApplication.processEvents()

                return

            # Check to make sure the data has the appropriate fields
            if not "library" in server_info or not "maintainer" in server_info:
                FreeCAD.Console.PrintError("OCCI ERROR: The OCCI repository is not presenting the correct data to be added.\r\n")

                # Make sure that the progress bar does not hang
                self.repos_progress_bar.setTextVisible(False)
                self.repos_progress_bar.setValue(0)
                QtCore.QCoreApplication.processEvents()

                return

            # Check to make sure this is not a duplicate entry
            if self.FindRepositoryRow(server_info['library'], server_info['maintainer']) != None:
                FreeCAD.Console.PrintWarning("OCCI: Duplicate repository entries are not permitted. If this repository server should not be a duplicate, contact the system administrator to make sure they do not have a conflicting name.\r\n")

                # Make sure that the progress bar does not hang
                self.repos_progress_bar.setTextVisible(False)
                self.repos_progress_bar.setValue(0)
                QtCore.QCoreApplication.processEvents()

                return

            # Find the end of the repositories table so we can add an entry
            row_count = self.repos_tbl.rowCount()
            new_row_index = 0
            for row_index in range(0, row_count + 1):
                # If we are past the end of the table, we need to add a new row
                if row_index == row_count:
                    self.repos_tbl.insertRow(row_count)
                    new_row_index = row_index

                # If there is nothing in the row, we know it is ready to be filled
                chkbox = self.repos_tbl.cellWidget(row_index, 0)
                if chkbox == None:
                    new_row_index = row_index
                    break

            # Add a new set of widgets to the last line
            new_chkbox = QtGui.QCheckBox(Checked=True)

            # The repository name text
            new_name_txt = QtGui.QLabel()
            new_name_txt.setAlignment(QtCore.Qt.AlignCenter)
            new_name_txt.setTextFormat(QtCore.Qt.RichText)
            new_name_txt.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            new_name_txt.setOpenExternalLinks(True)
            new_name_txt.setText('<a href="' + repo_url + '">' + server_info['library'] + '</a>')

            # The curator text
            new_curator_txt = QtGui.QLabel(text=server_info['maintainer'])
            new_curator_txt.setAlignment(QtCore.Qt.AlignCenter)

            # The remove button
            self.remove_buttons.append(QtGui.QPushButton(objectName=server_info['library'] + "_" + server_info['maintainer']))
            self.remove_buttons[new_row_index].setFlat(True)
            self.remove_buttons[new_row_index].setIcon(QtGui.QIcon(':/icons/delete.svg'))
            self.remove_buttons[new_row_index].clicked.connect(partial(self.RemoveRepository, self.remove_buttons[new_row_index]))

            # Add all the widgets to the table
            self.repos_tbl.setCellWidget(new_row_index, 0, new_chkbox)
            self.repos_tbl.setCellWidget(new_row_index, 1, new_name_txt)
            self.repos_tbl.setCellWidget(new_row_index, 2, new_curator_txt)
            self.repos_tbl.setCellWidget(new_row_index, 3, self.remove_buttons[new_row_index])

            # Save the new repository's information in the settings
            settings = QtCore.QSettings("OCCI", "occi-freecad-plugin")
            repo_list = settings.value('data/repo_list')
            if repo_url[-1] == "/":
                repo_url = repo_url[-1] = ""
            repo_list['list'].append({'use': True, 'library': server_info['library'], 'maintainer': server_info['maintainer'], 'models_url': repo_url})
            settings.setValue('data/repo_list', repo_list)
            settings.sync()
        elif response.status_code == 404:
            FreeCAD.Console.PrintError("OCCI ERROR: The OCCI repository URL provided does is not found.\r\n")
        elif response.status_code == 500:
            FreeCAD.Console.PrintError("OCCI ERROR: There was a server error while trying to load the OCCI repository data.\r\n")
        else:
            FreeCAD.Console.PrintError("OCCI ERROR: There was a general error while trying to load the OCCI repository data.\r\n")

        # Try to give the user a flash of 100%
        self.repos_progress_bar.setValue(100)
        QtCore.QCoreApplication.processEvents()

        # Let the user know that the get request is done
        self.repos_progress_bar.setTextVisible(False)
        self.repos_progress_bar.setValue(0)
        QtCore.QCoreApplication.processEvents()


    def LoadDefaults(self):
        """
        Loads the repository defaults from disk.
        """
        import yaml

        # Default settings file is YAML and is on disk
        defaults_file = FreeCAD.getUserAppDataDir() + "Mod/occi-freecad-plugin/defaults.yaml"

        # Open and parse the defaults file
        with open(defaults_file, 'r') as file:
            default_settings = yaml.safe_load(file)

        return default_settings


    def DoSearch(self):
        """
        Allows the user to hit the Enter key in the search box to search.
        """
        self.SearchComponents()


    def SearchComponents(self):
        """
        Searches the specified repositories for the given component.
        """
        from PySide import QtGui, QtCore
        import requests
        import json

        # Clear any previous results
        self.results_tbl.clearContents()
        self.ClearPreviousComponentResults()
        self.results_num_lbl.setText("Searching...")

        # Let the user know that something is going on
        self.search_progress_bar.setTextVisible(True)
        self.search_progress_bar.setValue(5)
        QtCore.QCoreApplication.processEvents()

        # Walk through each row of the repositories table and search them
        row_count = self.repos_tbl.rowCount()
        results_row = 0
        for row in range(0, row_count):
            # If there is something in the row, extract data from the row
            chkbox = self.repos_tbl.cellWidget(row, 0)
            if chkbox != None:
                # See if the user wants to use the current repo
                if chkbox.checkState() == QtCore.Qt.CheckState.Checked:
                    # Get the models URL text field
                    models_txt = self.repos_tbl.cellWidget(row, 1)
                    models_url = models_txt.text().split("\"")[1]

                    # Search the OCCI server for the search text
                    response = None
                    try:
                        # Let the user know progress is being made
                        self.search_progress_bar.setValue(10)
                        QtCore.QCoreApplication.processEvents()

                        # Request the search from the server
                        response = requests.get(models_url + '/search?q=' + self.search_txt.text())

                        # Let the user know how far through the search we have progressed
                        self.search_progress_bar.setValue(int(100 / (self.repos_tbl.rowCount() + 1)))
                        QtCore.QCoreApplication.processEvents()
                    except:
                        self.results_num_lbl.setText("Search error")

                        # Reset the progress bar so that it does not hang
                        self.search_progress_bar.setTextVisible(False)
                        self.search_progress_bar.setValue(0)
                        QtCore.QCoreApplication.processEvents()

                    # If there was a response, process it
                    if response != None and response.status_code == 200:
                        # Parse the JSON search results
                        self.json_search_results = json.loads(response.content)

                        # Let the user know how many search results there are
                        if (len(self.json_search_results) == 1):
                            self.results_num_lbl.setText(str(len(self.json_search_results)) + " result")
                        else:
                            self.results_num_lbl.setText(str(len(self.json_search_results)) + " results")

                        # Add all the search results to the table
                        for json_result in self.json_search_results:
                            # If we are past the end of the table, we need to add a new row
                            if results_row == self.results_tbl.rowCount():
                                self.results_tbl.insertRow(results_row)

                            # The component name field
                            cur_name_txt = QtGui.QLabel()
                            cur_name_txt.setAlignment(QtCore.Qt.AlignCenter)
                            # cur_name_txt.setTextFormat(QtCore.Qt.RichText)
                            # cur_name_txt.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
                            # cur_name_txt.setOpenExternalLinks(True)
                            cur_name_txt.setText(json_result['name'])
                            # cur_name_txt.setText('<a href="' + json_result['url'] + '">' + json_result['name'] + '</a>')
                            self.results_tbl.setCellWidget(results_row, 0, cur_name_txt)

                            # The component author field
                            cur_author_txt = QtGui.QLabel(json_result["author"])
                            self.results_tbl.setCellWidget(results_row, 1, cur_author_txt)

                            # The component description field
                            cur_description_txt = QtGui.QLabel(json_result["description"])
                            self.results_tbl.setCellWidget(results_row, 2, cur_description_txt)

                            results_row += 1
                    elif response.status_code == 404:
                        FreeCAD.Console.PrintError("OCCI ERROR: The model was not found in the OCCI repository.")
                    elif response.status_code == 500:
                        FreeCAD.Console.PrintError("OCCI ERROR: There was an error on the server that prevented the model from being generated. Please contact that server's administrator.")
                    else:
                        self.results_num_lbl.setText("Search error")

        # Give the user a flash of 100%
        self.search_progress_bar.setValue(100)
        QtCore.QCoreApplication.processEvents()

        # Let the user know that the request is finished
        self.search_progress_bar.setTextVisible(False)
        self.search_progress_bar.setValue(0)
        QtCore.QCoreApplication.processEvents()


    def BuildSTEPURL(self, base_url):
        """
        Builds the URL to grab the OCCI component STEP file with the
        parameter values set.
        """
        from PySide import QtGui

        download_url = base_url

        # Step through the parameters table, adding names and values
        for row_index in range(0, self.params_tbl.rowCount()):
            name_widget = self.params_tbl.cellWidget(row_index, 0)
            value_widget = self.params_tbl.cellWidget(row_index, 2)

            # Check to see if we have reached the last line
            if name_widget == None and value_widget == None:
                break
            else:
                # If this is the first parameter, add the question mark
                if row_index == 0:
                    download_url += "?"
                else:
                    download_url += "&"

                # We have to extract the value different ways from different controls
                if isinstance(value_widget, QtGui.QSpinBox) or isinstance(value_widget, QtGui.QDoubleSpinBox):
                    value = value_widget.value()
                else:
                    value = value_widget.text()

                download_url += name_widget.text().split("(")[0].strip().replace(" ", "+") + "=" + str(value)

        return download_url


    def FindSelectedComponent(self):
        """
        Finds the highlighted component in the components table and returns
        the name and author of a match. Returns None for both if nothing no
        row is highlighted.
        """
        name = None
        author = None

        # Get any selected rows
        selected_rows = self.results_tbl.selectedIndexes()
        if (len(selected_rows) > 0):
            # Simply grab the first selected row
            selected_row = self.results_tbl.selectedIndexes()[0].row()

            # If there is something in the row, extract data from the row
            name_txt = self.results_tbl.cellWidget(selected_row, 0)
            if name_txt != None:
                name = name_txt.text()
            author_txt = self.results_tbl.cellWidget(selected_row, 1)
            if author_txt != None:
                author = author_txt.text()

        return (name, author)


    def FindMatchingJSON(self, name, author):
        """
        Finds a match in the returned JSON result and returns it
        so that it can be queried.
        """

        # Make sure we have some search results loaded
        # If there are search results, look for the matching object in them
        if self.json_search_results != None:
            # Keeps track of any units used
            units_used = ""
            default_preset = {}

            # Look through all of the results
            for result in self.json_search_results:
                # See if we have a match
                if name != None and result['name'] == name and author != None and result['author'] == author:
                    return result

        # If no match was found, tell the caller by returning None
        return None


    def FindRepositoryRow(self, library, maintainer):
        """
        Finds a matching row in the repositories table.
        """

        # Step through each row of the repositories table
        for row_index in range(0, self.repos_tbl.rowCount()):
            # Try to get the controls in the table
            lib_txt = self.repos_tbl.cellWidget(row_index, 1)
            maint_txt = self.repos_tbl.cellWidget(row_index, 2)

            # If the library control is None, there is no need to check it
            if lib_txt == None or maint_txt == None:
                break

            # If the library and maintainer match, we assume we have a row match
            if library == lib_txt.text().split(">")[1].split("<")[0] and maintainer == maint_txt.text():
                return row_index

        return None


    def DownloadModel(self, base_url):
        """
        Handles the task of downloading an OCCI component.
        """
        import tempfile
        import requests
        from PySide import QtCore

        # Let the user know that something is going on
        self.search_progress_bar.setTextVisible(True)
        self.search_progress_bar.setValue(5)
        QtCore.QCoreApplication.processEvents()

        # Get the STEP download URL with current parameters
        download_url = self.BuildSTEPURL(base_url)

        # We need a temporary file to download the STEP file into
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.step')

        # Let the user know that something is going on
        self.search_progress_bar.setValue(10)
        QtCore.QCoreApplication.processEvents()

        # A progress indicator
        progress = 10

        # Request the STEP download from the OCCI server and account for large file size
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            if response.status_code == 200:
                with open(self.temp_file.name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        # Let the user know that work is being done
                        progress += 10
                        self.search_progress_bar.setTextVisible(True)
                        self.search_progress_bar.setValue(progress)
                        QtCore.QCoreApplication.processEvents()

                        f.write(chunk)
            elif response.status_code == 404:
                FreeCAD.Console.PrintError("OCCI ERROR: The model you have requested does not seem to exist on the server.\r\n")
            elif response.status_code == 500:
                FreeCAD.Console.PrintError("OCCI ERROR: There was an error on the server that prevented the model from being downloaded. Please contact the server administrator.\r\n")

        # Give the user a flash of 100% complete
        self.search_progress_bar.setValue(100)
        QtCore.QCoreApplication.processEvents()

        # Let the user know that the request is done
        self.search_progress_bar.setTextVisible(False)
        self.search_progress_bar.setValue(0)
        QtCore.QCoreApplication.processEvents()

        return self.temp_file.name


    def LoadComponent(self):
        """
        Loads a specific component into the current document.
        """

        # Get the information for the selected component
        name, author = self.FindSelectedComponent()
        json_result = self.FindMatchingJSON(name, author)

        # Make sure there was a row selected
        if name != None and author != None:
            step_file_path = self.DownloadModel(json_result['url'])

            # If there is not an active document, add one
            is_new_doc = False
            ad = FreeCAD.activeDocument()
            if ad == None:
                FreeCAD.newDocument("untitled occi component")
                ad = FreeCAD.activeDocument()
                is_new_doc = True

            # Add a feature object and load the step into it
            new_feature = ad.addObject("Part::Feature", name)
            new_feature.Label = name + "_" + author
            new_feature.ViewObject.ShapeColor = (0.0, 1.0, 0.5)
            new_feature.ViewObject.Transparency = 0

            # Load the STEP file into a FreeCAD Shape to display it
            import Part
            new_shape = Part.Shape()
            new_shape.read(step_file_path)
            new_feature.Shape = new_shape
            ad.recompute()

            # If we just created a document, then auto-fit everything
            if is_new_doc:
                Gui.activeDocument().activeView().viewIsometric()
                Gui.SendMsgToActiveView("ViewFit")

        else:
            FreeCAD.Console.PrintMessage("OCCI: Please select a component in order to configure and add it.\r\n")


    def UseCheckboxChanged(self, checkbox, state):
        """
        Called when a use checkbox on a repository entry is changed.
        """
        from PySide.QtCore import QSettings

        # We need to extract the library and maintainer to match this checkbox to its repo row
        library = checkbox.objectName().split("_")[0]
        maintainer = checkbox.objectName().split("_")[1]

        # Try to find the matching row index
        row_index = self.FindRepositoryRow(library, maintainer)

        # Make sure there was a match
        if row_index != None:
            # Pull the repo list dictionary from the settings
            settings = QSettings("OCCI", "occi-freecad-plugin")
            repo_list = settings.value('data/repo_list')
            repo_list['list'][row_index]['use'] = checkbox.isChecked()
            settings.setValue('data/repo_list', repo_list)
            settings.sync()


    def CheckBoxChanged(self):
        """
        The state of the Auto Update checkbox needs to be saved.
        """
        from PySide.QtCore import QSettings

        # Make sure this method has access to the settings
        settings = QSettings("OCCI", "occi-freecad-plugin")

        settings.setValue('ui/auto_update', 'yes' if self.auto_update_chk.isChecked() else 'no')
        settings.sync()


    def UpdateModelWithParameters(self):
        """
        Handles auto-updating of the model when a parameter is changed.
        """

        # Make sure the auto-update checkbox is checked
        if self.auto_update_chk.isChecked():
            self.UpdateComponent()


    def UpdateComponent(self):
        """
        Handles the task of updating a component that is already in the view.
        """

        # If there is no active document, there is nothing to update
        ad = FreeCAD.activeDocument()
        if ad == None:
            self.LoadComponent()
            return

        # Get the information for the selected component
        name, author = self.FindSelectedComponent()
        json_result = self.FindMatchingJSON(name, author)

        # Make sure there was a row selected
        if name != None and author != None:
            step_file_path = self.DownloadModel(json_result['url'])

            # Find the the matching object in the active document
            feature = ad.getObjectsByLabel(name + "_" + author)[0]
            if feature != None:
                import Part
                new_shape = Part.Shape()
                new_shape.read(step_file_path)
                feature.Shape = new_shape
                ad.recompute()


    def ClearResultsTableHighlights(self):
        """
        Clears the table of highlights because we use a manual highlight method
        to avoid using a custom renderer.
        """

        # Walk through all the cells
        for row_index in range(0, self.results_tbl.rowCount()):
            # Reset the first column's highlight
            if self.results_tbl.cellWidget(row_index, 0) != None:
                self.results_tbl.cellWidget(row_index, 0).setStyleSheet("background-color:#FFFFFF")

            # Reset the second column's highlight
            if self.results_tbl.cellWidget(row_index, 1) != None:
                self.results_tbl.cellWidget(row_index, 1).setStyleSheet("background-color:#FFFFFF")

            # Reset the third column's highlight
            if self.results_tbl.cellWidget(row_index, 2) != None:
                self.results_tbl.cellWidget(row_index, 2).setStyleSheet("background-color:#FFFFFF")


    def RemoveRepository(self, button):
        """
        Handles the removal of a repository from the repositories table.
        """
        from PySide.QtCore import QSettings

        # Retrieve the row index
        if button.objectName() != None:
            library = button.objectName().split("_")[0]
            maintainer = button.objectName().split("_")[1]

            # Try to find the matching row index
            row_index = self.FindRepositoryRow(library, maintainer)

            # Remove the row from the table and the array of buttons
            if row_index != None:
                self.repos_tbl.removeRow(row_index)
                self.remove_buttons.pop(row_index)

                # Remove the matching setting
                settings = QSettings("OCCI", "occi-freecad-plugin")
                repo_list = settings.value('data/repo_list')
                repo_list['list'].pop(row_index)
                settings.setValue('data/repo_list', repo_list)
                settings.sync()


    def RemovePreviousPresets(self):
        """
        Handles the task of clearing out old preset buttons from the presets layout.
        """

        children = []
        for i in range(self.presets_layout.count()):
            child = self.presets_layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()


    def ClearPreviousComponentResults(self):
        """
        Wrapper for all the parameter data clean-up methods when a new search is
        conducted or new parameter selected.
        """
        self.ClearResultsTableHighlights()
        self.selected_comp_lbl.setText("No component selected")
        self.model_info_lbl.setText("No model loaded")
        self.source_info_lbl.setText("No model loaded")
        self.presets_info_lbl.setVisible(True)
        self.params_tbl.clearContents()  # Clear any previous parameter table contents
        self.RemovePreviousPresets()  # Clear any previous parameters from the table
        self.presets_controls.clear()
        self.presets.clear()


    def HandlePresetButton(self, button):
        """
        Handles loading the presets associated with a preset button into the controls.
        """

        # We stored the key to the preset in the object name of the button
        preset_key = button.objectName()

        # Get the preset values back out of global storage and step through each one
        for key in self.presets[preset_key].keys():
            # Search the parameters table to look for a matching name
            for row_index in range(0, self.params_tbl.rowCount()):
                # Get the widget and protect against a blank row
                widget = self.params_tbl.cellWidget(row_index, 0)
                if widget == None:
                    break

                # The parameter name
                param_name = widget.text().split("(")[0].strip()

                # If there is a match, set the corresponding value control
                if param_name == key:
                    # The value widget should be in the third column (index starts at 0)
                    value_widget = self.params_tbl.cellWidget(row_index, 2)
                    value_widget.setValue(self.presets[preset_key][key])

                    # We found what we need, exit the loop
                    break


    def LoadParameters(self):
        """
        Loads the parameters for the selected component in the component search results table.
        """
        from functools import partial
        from PySide import QtGui, QtCore

        # The stylesheet of the highlighted row
        highlighted_row_style = "background-color:#AAAAAA;"

        # Clear any previous row highlights and all of the label data
        self.ClearPreviousComponentResults()

        # Make sure there really is some sort of selection
        if len(self.results_tbl.selectedRanges()) > 0:
            # Get the selected row so we can highlight/use it
            row_index = self.results_tbl.selectedRanges()[0].topRow()

            # Highlight rows manually only if they have widgets in them
            if self.results_tbl.cellWidget(row_index, 0) != None:
                self.results_tbl.cellWidget(row_index, 0).setStyleSheet(highlighted_row_style)
            if self.results_tbl.cellWidget(row_index, 1) != None:
                self.results_tbl.cellWidget(row_index, 1).setStyleSheet(highlighted_row_style)
            if self.results_tbl.cellWidget(row_index, 2) != None:
                self.results_tbl.cellWidget(row_index, 2).setStyleSheet(highlighted_row_style)

            # Get the name and author from the selected row
            name_txt = None
            author_txt = None
            if self.results_tbl.cellWidget(row_index, 0) != None:
                name_txt = self.results_tbl.cellWidget(row_index, 0).text()
            if  self.results_tbl.cellWidget(row_index, 1) != None:
                author_txt = self.results_tbl.cellWidget(row_index, 1).text()

        # Make sure we have some search results loaded
        # If there are search results, look for the matching object in them
        name, author = self.FindSelectedComponent()
        result = self.FindMatchingJSON(name, author)
        if result != None:
            units_used = ""
            default_preset = {}

            # Step through all of the parameters and add them to the table
            row_index = 0
            for param in result['params'].keys():
                # If we are past the end of the table, we need to add a new row
                if row_index == self.params_tbl.rowCount():
                    self.params_tbl.insertRow(row_index)

                # Save the default for each parameter
                default_preset[param] = result['params'][param]['default']

                if not result['params'][param]['units'] in units_used:
                    if units_used != "":
                        units_used += "," + result['params'][param]['units']
                    else:
                        units_used += result['params'][param]['units']

                # Add the name widget in the first column
                name_lbl = QtGui.QLabel(text=result['params'][param]['name'] + " (" + result['params'][param]['units'] + ")")
                name_lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.params_tbl.setCellWidget(row_index, 0, name_lbl)

                # Add the description widget in the second column
                desc_lbl = QtGui.QLabel(text=result['description'])
                desc_lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.params_tbl.setCellWidget(row_index, 1, desc_lbl)

                # Add the value widget in the last column
                if result['params'][param]['type'] == 'number' and isinstance(result['params'][param]['default'], int):
                    # An integer spin number box
                    value_widget = QtGui.QSpinBox()
                    value_widget.setValue(int(result['params'][param]['default']))
                    value_widget.setRange(int(result['params'][param]['start']), int(result['params'][param]['end']))
                    value_widget.setSingleStep(int(result['params'][param]['step']))
                    value_widget.textChanged.connect(self.UpdateModelWithParameters)
                    self.params_tbl.setCellWidget(row_index, 2, value_widget)
                elif result['params'][param]['type'] == 'number' and isinstance(result['params'][param]['default'], float):
                    # A float spin number box
                    value_widget = QtGui.QDoubleSpinBox()
                    value_widget.setValue(float(result['params'][param]['default']))
                    value_widget.setRange(float(result['params'][param]['start']), float(result['params'][param]['end']))
                    value_widget.setSingleStep(float(result['params'][param]['step']))
                    value_widget.textChanged.connect(self.UpdateModelWithParameters)
                    self.params_tbl.setCellWidget(row_index, 2, value_widget)
                elif result['params'][param]['type'] == 'text':
                    # A text field
                    value_widget = QtGui.QLineEdit()
                    value_widget.setPlaceholderText("Parameter Text")
                    value_widget.textChanged.connect(self.UpdateModelWithParameters)
                    self.params_tbl.setCellWidget(row_index, 2, value_widget)

                row_index += 1

            # Let the user know what was selected
            self.selected_comp_lbl.setText('"' + result["name"] + '" component selected')
            self.model_info_lbl.setText("Code CAD engine: " + result['script_cad_language'] + " - Author: " + result['author'] + " - Units: " + units_used)
            self.source_info_lbl.setText('Source: <a href="' + result["url"] + '">link</a>')

            # There should always be a default preset
            self.presets_info_lbl.setVisible(False)
            default_btn = QtGui.QPushButton(text="Default", objectName="default")
            self.presets["default"] = default_preset
            default_btn.clicked.connect(partial(self.HandlePresetButton, default_btn))
            self.presets_layout.addWidget(default_btn, 0, 0, 1, 1, QtCore.Qt.AlignCenter)

            # Step through all of the other presets and add them
            row = 0
            col = 1
            for preset in result["param_presets"].keys():
                # Advance to the next row, if needed
                if col % 4 == 0:
                    row += 1
                    col = -1

                col += 1

                # Object name for button based on row/column so we can use it as a key
                self.presets_controls.append(QtGui.QPushButton(text=preset, objectName="btn_" + str(row) + "_" + str(col)))

                # Save the preset associated with this button
                self.presets["btn_" + str(row) + "_" + str(col)] = result["param_presets"][preset]

                # Pass this button to its signal slot
                self.presets_controls[-1].clicked.connect(partial(self.HandlePresetButton, self.presets_controls[-1]))

                self.presets_layout.addWidget(self.presets_controls[-1], row, col, 1, 1, QtCore.Qt.AlignCenter)


Gui.addWorkbench(OCCIWorkbench())
