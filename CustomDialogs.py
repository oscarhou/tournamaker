from PyQt4 import QtGui, QtCore
from model import TournamentModel, GenericModel
class MessageDialog(QtGui.QMessageBox):
    def __init__(self, parentWidget, text, standard_button_mask):
        super(MessageDialog, self).__init__(parentWidget)
        self.setText(text)
        self.setStandardButtons(standard_button_mask)
        self.exec_()

class AddPlayerDialog(QtGui.QDialog):

    def __init__(self, parentWidget):
        super(AddPlayerDialog, self).__init__(parentWidget)
        layout = QtGui.QFormLayout()

        # set up buttons and input
        self.first_name = QtGui.QLineEdit()
        self.last_name = QtGui.QLineEdit()
        self.nickname = QtGui.QLineEdit()
        self.phone = QtGui.QLineEdit()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")

        # register buttons to functions
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        layout.addRow("First Name:", self.first_name)
        layout.addRow("Last Name:", self.last_name)
        layout.addRow("Nickname:", self.nickname)
        layout.addRow("Phone:", self.phone)
        layout.addRow(self.ok_button, self.cancel_button)
        self.setLayout(layout)

    def get_form_data(self):
      return {'first_name' : str(self.first_name.text()),
              'last_name' : str(self.last_name.text()),
              'nickname' : str(self.nickname.text()),
              'phone' : str(self.phone.text())}

    def ok_clicked(self):
        self.accept()

    def cancel_clicked(self):
        self.close()

class EnrollPlayerDialog(QtGui.QDialog):

    def __init__(self, non_enrolled, enrolled):
        super(EnrollPlayerDialog, self).__init__()

        self.enrolled_players = []
        for player in enrolled:
            self.enrolled_players.append((player.id, player.nickname))

        self.non_enrolled_players = []
        for player in non_enrolled:
            self.non_enrolled_players.append((player.id,player.nickname))

        layout = QtGui.QGridLayout()
        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")

        # register buttons to functions
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        self.enrolled_player_list_view = QtGui.QListView(self)
        self.enrolled_player_list_model = GenericModel.Generic(self.enrolled_player_list_view)
        self.enrolled_player_list_view.doubleClicked.connect(self.enrolled_player_double_clicked)

        self.enrolled_player_list_model.add_items(self.enrolled_players)
        self.enrolled_player_list_view.setModel(self.enrolled_player_list_model)

        # for non enrolled players
        self.non_enrolled_player_list_view = QtGui.QListView(self)
        self.non_enrolled_player_list_model = GenericModel.Generic(self.non_enrolled_player_list_view)
        self.non_enrolled_player_list_view.doubleClicked.connect(self.non_enrolled_player_double_clicked)

        self.non_enrolled_player_list_model.add_items(self.non_enrolled_players)
        self.non_enrolled_player_list_view.setModel(self.non_enrolled_player_list_model)

        layout.addWidget(QtGui.QLabel("Non-Enrolled"), 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel("Enrolled"), 1, 2, 1, 1)
        layout.addWidget(self.non_enrolled_player_list_view, 2, 1, 1, 1)
        layout.addWidget(self.enrolled_player_list_view, 2, 2, 1, 1)
        layout.addWidget(self.ok_button, 3, 1, 1, 1)
        layout.addWidget(self.cancel_button, 3, 2, 1, 1)
        self.setLayout(layout)

    def non_enrolled_player_double_clicked(self, model_index):
        self.take_and_move(
            self.non_enrolled_player_list_model,
            self.enrolled_player_list_model,
            model_index)

    def enrolled_player_double_clicked(self, model_index):
        self.take_and_move(
            self.enrolled_player_list_model,
            self.non_enrolled_player_list_model,
            model_index)

    def take_and_move(self, from_model, to_model, model_index):
        item = QtGui.QStandardItem(from_model.itemFromIndex(model_index))
        from_model.removeRow(model_index.row())
        data = item.data(QtCore.Qt.UserRole).toPyObject()
        to_model.appendRow(item)

    def get_id_list(self, model):
        id_list = []
        for index in range(model.rowCount()):
            item = model.item(index)
            # Get the object id from the UserRole field
            id_list.append(item.data(QtCore.Qt.UserRole).toPyObject())
        return id_list

    def get_lists(self):
        enrolled_id_list = self.get_id_list(self.enrolled_player_list_model)
        non_enrolled_id_list = self.get_id_list(self.non_enrolled_player_list_model)
        return (enrolled_id_list, non_enrolled_id_list)

    def ok_clicked(self):
        self.accept()

    def cancel_clicked(self):
        self.close()


