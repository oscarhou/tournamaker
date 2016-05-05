from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

# FIXME all these classes can be combined
class DialogButton(QtGui.QPushButton):
    value_changed_trigger = pyqtSignal()
    def __init__(self, name, dialog_text, parentWidget):
        super(DialogButton, self).__init__()
        self.parentWidget = parentWidget
        self.setText(name)
        self.name = name
        self.dialog_text = dialog_text
        self.dialog_output_func = None
        self.setEnabled(False)
        self.clicked.connect(self.clicked_button)

    def register_callback(self, func):
        self.dialog_output_func = func

    def clicked_button(self):
        text, ok = QtGui.QInputDialog.getText(self.parentWidget, self.name, self.dialog_text)
        if ok and self.dialog_output_func:
            self.dialog_output_func(str(text))

class AddPlayerListButton(QtGui.QPushButton):
    def __init__(self, parentWidget):
        super(AddPlayerListButton, self).__init__()
        self.target_player_list = None
        self.parentWidget = parentWidget
        self.clicked.connect(self.open_file_dialog)
        self.setText("Add Player List")
        self.handler_func = None
        self.setEnabled(True)

    def register_handler_func(self, func):
        self.handler_func = func

    def open_file_dialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        # call handler function when it is updated
        if fname:
            self.handler_func(fname)

class CreateTournamentButton(QtGui.QPushButton):
    def __init__(self, parentWidget):
        super(CreateTournamentButton, self).__init__()
        self.parentWidget = parentWidget
        self.setText("Create Tournament")
        self.handler_func = None
        self.clicked.connect(self.create_new_tournament)

    def register_handler_func(self, func):
        self.handler_func = func

    def create_new_tournament(self):
        text, ok = QtGui.QInputDialog.getText(self.parentWidget, 'Create Tournament', 'Enter tournament name:')

        if ok:
            self.handler_func(str(text))

