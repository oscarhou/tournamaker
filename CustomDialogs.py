from PyQt4 import QtGui, QtCore
from model import TournamentModel, GenericModel
from model_helpers import get_id_list
from PyQt4.QtCore import pyqtSignal
import SqlTypes

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

        self.enrolled_player_list_model.add_items(self.enrolled_players)
        self.enrolled_player_list_view.setModel(self.enrolled_player_list_model)

        # for non enrolled players
        self.non_enrolled_player_list_view = QtGui.QListView(self)
        self.non_enrolled_player_list_model = GenericModel.Generic(self.non_enrolled_player_list_view)

        self.non_enrolled_player_list_model.add_items(self.non_enrolled_players)
        self.non_enrolled_player_list_view.setModel(self.non_enrolled_player_list_model)

        # set up swapper class
        self.swapper = QModelSwapper(self.enrolled_player_list_model, self.non_enrolled_player_list_model)
        self.non_enrolled_player_list_view.doubleClicked.connect(self.swapper.second_double_clicked)
        self.enrolled_player_list_view.doubleClicked.connect(self.swapper.first_double_clicked)

        layout.addWidget(QtGui.QLabel("Non-Enrolled"), 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel("Enrolled"), 1, 2, 1, 1)
        layout.addWidget(self.non_enrolled_player_list_view, 2, 1, 1, 1)
        layout.addWidget(self.enrolled_player_list_view, 2, 2, 1, 1)
        layout.addWidget(self.ok_button, 3, 1, 1, 1)
        layout.addWidget(self.cancel_button, 3, 2, 1, 1)
        self.setLayout(layout)

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

class QModelSwapper(QtCore.QObject):
    swapped = pyqtSignal()
    def __init__(self, first_model, second_model):
        super(QModelSwapper, self).__init__()
        self.first_model = first_model
        self.second_model = second_model

    def first_double_clicked(self, model_index):
        self.take_and_move(
            self.first_model,
            self.second_model,
            model_index)

    def second_double_clicked(self, model_index):
        self.take_and_move(
            self.second_model,
            self.first_model,
            model_index)

    def take_and_move(self, from_model, to_model, model_index):
        item = QtGui.QStandardItem(from_model.itemFromIndex(model_index))
        from_model.removeRow(model_index.row())
        data = item.data(QtCore.Qt.UserRole).toPyObject()
        to_model.appendRow(item)
        self.swapped.emit()

class ManageGroupDialog(QtGui.QDialog):
    class GroupItem():
        def __init__(group_id=None, group=[]):
            self.group_id = group_id
            self.group = group

    def __init__(self, enrolled_players, groups):
        super(ManageGroupDialog, self).__init__()

        # copy the input groups
        self.groups_list = list(groups)

        # show groups
        self.groups_view = QtGui.QTableView()
        self.groups_model = GenericModel.TableModel(["Players"])
        self.set_groups_table()
        self.groups_view.setModel(self.groups_model)
        self.groups_view.clicked.connect(self.update_group_members_view)
        self.groups_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.groups_view.horizontalHeader().setStretchLastSection(True)

        self.enrolled_player_list_view = QtGui.QListView(self)
        self.enrolled_players_list_model = GenericModel.Generic(self.enrolled_player_list_view)
        self.enrolled_player_list_view.setModel(self.enrolled_players_list_model)

        self.set_model_players(enrolled_players, self.enrolled_players_list_model)

        self.ok_button = QtGui.QPushButton("Ok")
        self.cancel_button = QtGui.QPushButton("Cancel")

        # register buttons to functions
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.create_group_button = QtGui.QPushButton("Create Group")
        self.create_group_button.clicked.connect(self.add_new_group)

        # show players in groups
        self.group_players_list = QtGui.QListView(self)
        self.group_players_list_model = GenericModel.Generic(self.group_players_list)
        self.group_players_list.setModel(self.group_players_list_model)

        # swapper
        self.swapper = QModelSwapper(self.enrolled_players_list_model, self.group_players_list_model)
        self.enrolled_player_list_view.doubleClicked.connect(self.swapper.first_double_clicked)
        self.group_players_list.doubleClicked.connect(self.swapper.second_double_clicked)
        self.swapper.swapped.connect(self.update_players_models)

        # set up the layout
        h_layout = QtGui.QHBoxLayout()
        h_layout.addWidget(self.enrolled_player_list_view)
        v_layout = QtGui.QVBoxLayout()
        v_layout.addWidget(QtGui.QLabel("Groups"))
        v_layout.addWidget(self.create_group_button)
        v_layout.addWidget(self.groups_view)
        v_layout.addWidget(QtGui.QLabel("Group Members"))
        v_layout.addWidget(self.group_players_list)
        v_layout.addWidget(self.ok_button)
        v_layout.addWidget(self.cancel_button)
        h_layout.addLayout(v_layout)
        self.setLayout(h_layout)

    def get_group_members_string(self, players):
        players_str = ""
        count = 0
        for player in players:
            players_str += "{}".format(player.nickname)
            count += 1
            if count < len(item.players):
                players_str += ','
        return players_str

    def set_groups_table(self):
        groups = []
        for item in self.groups_list:
            groups.append(self.get_group_members_string(item.players))

        self.groups_model.setData(groups, role=QtCore.Qt.DisplayRole)
        self.groups_model.setData(self.groups_list, role=QtCore.Qt.UserRole)
        self.groups_view.resizeColumnsToContents()

    def set_model_players(self, groupless_players, model):
        display_tuple_list = []
        for player in groupless_players:
            display_tuple_list.append((player.id, player.nickname))

        # FIXME: gonna be a bug
        model.add_items(display_tuple_list)

    # called when a group is clicked, update the group members view
    def update_group_members_view(self, model_index):
        self.group_players_list_model.clear()
        selected = self.groups_model.data(self.groups_view.selectedIndexes()[0], QtCore.Qt.UserRole)
        display_player_tuple = []
        for player in selected.players:
            display_player_tuple.append((player.id, player.nickname))

        # update group member list view
        self.group_players_list_model.add_items(display_player_tuple)

    def update_players_models(self):
        selected_data = self.groups_model.data(self.groups_view.selectedIndexes()[0], QtCore.Qt.UserRole)
        current_group_players_id = self.get_list(self.group_players_list_model, QtCore.Qt.UserRole)
        current_group_players_names = self.get_list(self.group_players_list_model, QtCore.Qt.DisplayRole)

        player_list = []
        for count in xrange(len(current_group_players_id)):
            player_list.append(SqlTypes.Player(id=current_group_players_id[count], nickname=current_group_players_names[count]))

        selected_data.players = player_list

        # I FUCKING HATE THIS CODE
        players_str = "None"
        if len(current_group_players_names) > 0:
          players_str = ""
          count = 0
          for player in current_group_players_names:
              players_str += "{}".format(player)
              count += 1
              if count < len(current_group_players_names):
                  players_str += ','

        self.groups_model.setRow(self.groups_view.selectedIndexes()[0].row(), [players_str], QtCore.Qt.DisplayRole)
        self.groups_model.setRow(self.groups_view.selectedIndexes()[0].row(), selected_data, QtCore.Qt.UserRole)


        return
        # first see if any players have been removed
        for player in selected.players:
            found = False
            for group_player in current_group_players:
                # if found then do nothing
                if group_player == player.id:
                   current_group_players.remove(group_player)
                   found = True
                   break 

            # if this player was not found then we have to remove it
            if not found:
                selected.players.remove(player)

    def ok_clicked(self):
        self.accept()

    def cancel_clicked(self):
        self.close()

    def add_new_group(self):
        self.groups_model.add_row(["None"], QtCore.Qt.DisplayRole)
        self.groups_model.add_row(SqlTypes.Group(), QtCore.Qt.UserRole)

    def get_list(self, model, role=QtCore.Qt.DisplayRole):
        id_list = []
        for index in range(model.rowCount()):
            item = model.item(index)
            # Get the object id from the UserRole field
            id_list.append(item.data(role).toPyObject())
        return id_list

    def get_data(self):
       return self.groups_list, self.get_id_list(self.enrolled_players_list_model)
