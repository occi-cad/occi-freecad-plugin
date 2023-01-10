from PySide import QtGui, QtCore

class CollapsibleWidget(QtGui.QWidget):
    """
    Class which defines a custom Qt widget that collapses/expands when clicked,
    hiding/showing its child controls.
    """

    def __init__(self, title="Collapsible Widget", parent=None):
        """
        Sets this control up for use, with a custom label at the top.
        """
        super(CollapsibleWidget, self).__init__(parent)

        # Styling for the toggle button
        self.toggle_button_css = "border:none;background-color:#D8D8D8;font-size: 14px;"

        # Get the parent width, if it exists
        if parent != None:
            par_width = parent.width

        # A VBox layout is needed to arrange the controls top to bottom
        main_layout = QtGui.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        # We need a collapse/expand button at the very top of this widget
        self.toggle_widget = QtGui.QWidget()
        self.toggle_widget.setStyleSheet(self.toggle_button_css)
        self.toggle_widget.setMaximumHeight(30)
        self.toggle_layout = QtGui.QGridLayout()

        # The text button
        self.toggle_button = QtGui.QToolButton(text=title)
        self.toggle_button.setStyleSheet(self.toggle_button_css)
        self.toggle_button.clicked.connect(self.toggle_widgets)
        self.toggle_layout.addWidget(self.toggle_button, 0, 0, 1, 11, QtCore.Qt.AlignCenter)

        # The arrow that shows the toggled state
        self.toggle_button_arrow = QtGui.QToolButton(text=title)
        self.toggle_button_arrow.setStyleSheet(self.toggle_button_css)
        self.toggle_button_arrow.setArrowType(QtGui.Qt.UpArrow)
        self.toggle_button_arrow.clicked.connect(self.toggle_widgets)
        self.toggle_layout.addWidget(self.toggle_button_arrow, 0, 12, 1, 1)


        # Add the toggle button group
        self.toggle_widget.setLayout(self.toggle_layout)
        main_layout.addWidget(self.toggle_widget)

        # Create the collapsible layout
        self.container_layout = QtGui.QVBoxLayout()
        self.container_widget = QtGui.QWidget()
        self.container_widget.setLayout(self.container_layout)
        main_layout.addWidget(self.container_widget)

        self.setLayout(main_layout)

        self.is_hidden = False


    def add_widget(self, widget):
        """
        Wrapper of the Qt method addWidget which allows QtWidgets to be added
        to the internal layout of this widget.
        """
        self.container_layout.addWidget(widget)

        # Work-around to make sure the layout looks correct to the user
        self.toggle_widgets()
        self.toggle_widgets()


    def add_layout(self, layout):
        """
        Wrapper of the Qt method addLayout which allows QLayouts to be nested.
        """
        self.container_layout.addLayout(layout)


    def toggle_widgets(self):
        """
        Handles resizing the control so that all of its child controls except
        for the toggle button are hidden.
        """

        # If we need to hide, set height to 0 and give a visual indication with the arrow
        if self.is_hidden == True:
            height = self.container_layout.sizeHint().height()
            self.toggle_button_arrow.setArrowType(QtGui.Qt.UpArrow)
            self.is_hidden = False
        else:
            height = 0
            self.toggle_button_arrow.setArrowType(QtGui.Qt.DownArrow)
            self.is_hidden = True

        # Set the height of the widget
        self.container_widget.setFixedHeight(height)
