from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal
from model import GenericModel

class CreateGroup(QtGui.QDialog):
    def __init__(self, enrolled_players, groups):
        super(CreateGroup, self).__init__()

        # put into dict for easier access
        self.groups_dict = {}
        for group in groups:
            self.groups_dict[group.id] = group

        # show groups
        self.groups_view = QtGui.QTableView()
        self.groups_model = GenericModel.TableModel(["Players"])
        self.set_groups_table()
        self.groups_view.setModel(self.groups_model)
        self.groups_view.clicked.connect(self.update_group_members_view)

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

        # show players in groups
        self.group_players_list = QtGui.QListView(self)

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

    def set_groups_table(self):
        groups = []
        ids = []
        for key, item in self.groups_dict.iteritems():
            ids.append(key)
            players_str = ""
            count = 0

            # write the group members
            for player in item.players:
                players_str += "{}".format(player.nickname)
                count += 1
                if count < len(item.players):
                    players_str += ','

            groups.append(players_str)

        self.groups_model.setData(groups, role=QtCore.Qt.DisplayRole)
        self.groups_model.setData(ids, role=QtCore.Qt.UserRole)
        self.groups_view.resizeColumnsToContents()

    def set_model_players(self, groupless_players, model):
        display_tuple_list = []
        for player in groupless_players:
            display_tuple_list.append((player.id, player.nickname))

        # FIXME: gonna be a bug
        model.add_items(display_tuple_list)

    def update_group_members_view(self):
        return

    def ok_clicked(self):
        self.accept()

    def cancel_clicked(self):
        self.close()

    def get_data(self):
        print "getting dat"


