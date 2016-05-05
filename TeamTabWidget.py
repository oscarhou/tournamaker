from PyQt4 import QtGui, QtCore
from model import GenericModel
from TournamentPlayerWidget import TournamentPlayerWidget
from Widgets import TeamWinLossWidget

class TeamsWidget(QtGui.QWidget):
    def __init__(self, model=None, parent=None, round_id=None):
        super(TeamsWidget, self).__init__()

        self.teams_count = 0
        self.get_teams_func = None
        self.export_func = None
        self.round_id = round_id
        teams_tab_layout = QtGui.QGridLayout(self)

        #teams model
        self.teams_model = GenericModel.TableModel(["Name", "Players", "Opponent", "Win/Loss"])
        self.teams_view = QtGui.QTableView()
        self.teams_view.setModel(self.teams_model)
        self.teams_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.teams_view.horizontalHeader().setStretchLastSection(True)
        self.teams_view.clicked.connect(self.team_clicked)

        # player tab
        self.player_list_model = GenericModel.TableModel(["Player Nickname"])
        self.players_widget = TournamentPlayerWidget(self.player_list_model, round_id=round_id)
        self.players_widget.set_model(self.player_list_model)

        #button for creating teams
        self.generate_teams_button = QtGui.QPushButton()
        self.generate_teams_button.setText("Generate Teams")
        self.generate_teams_button.clicked.connect(self.generate_teams)

        #button for creating teams
        self.export_teams_button = QtGui.QPushButton()
        self.export_teams_button.setText("Export")
        self.export_teams_button.clicked.connect(self.export_teams)

        # Forms
        self.team_win_loss_widget = TeamWinLossWidget()
        self.team_win_loss_widget.register_win_lose_click(self.team_win_loss_clicked)

        self.team_win_loss_handler_func = None

        #add widgets to layout
        teams_tab_layout.addWidget(self.players_widget, 1, 1, 3, 1)
        teams_tab_layout.addWidget(self.teams_view, 1, 2, 1, 1)
        teams_tab_layout.addWidget(self.generate_teams_button, 2, 2)
        teams_tab_layout.addWidget(self.export_teams_button, 3, 2)
        teams_tab_layout.addWidget(self.team_win_loss_widget, 1, 3, 3, 1)

        self.setLayout(teams_tab_layout)
        self.show()

    def players_reload(self, data):
        self.players_widget.reload(data)

    def set_players_model(self, model):
        self.players_widget.set_model(model)

    def register_enroll_player_clicked(self, func):
        self.players_widget.register_enroll_player_clicked(func)

    def register_player_export_clicked(self,func):
        self.players_widget.register_export_clicked(func)

    def register_team_clicked(self, func):
        self.team_clicked_func = func

    def team_win_loss_clicked(self, team_won):
        team_id = self.teams_model.data(
            self.teams_view.selectedIndexes()[0], QtCore.Qt.UserRole)

        self.team_win_loss_handler_func(team_id, team_won)

    def register_win_lose_click(self, func):
        self.team_win_loss_handler_func = func

    def team_clicked(self, model_index):
        team_id = self.teams_model.data(
            self.teams_view.selectedIndexes()[0], QtCore.Qt.DisplayRole)
        opponent_name = self.teams_model.getRow(model_index, QtCore.Qt.DisplayRole)[2]
        self.team_win_loss_widget.set_opponent(opponent_name)

    def teams_reload(self,ids, data):
        self.teams_model.setData(data, role=QtCore.Qt.DisplayRole)
        self.teams_model.setData(ids, role=QtCore.Qt.UserRole)
        self.teams_view.resizeColumnsToContents()

    def update_team_win_loss(self, opponent):
        self.team_win_loss_widget.set_opponent(opponent)

    def generate_teams(self):
        if self.teams_count > 0:
            quit_msg = "Are you sure you want to regenerate teams?"
            reply = QtGui.QMessageBox.question(self, 'Message',
                quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.get_teams_func(self.round_id)
        else:
          self.get_teams_func(self.round_id)

    def register_generate_teams_clicked(self, func):
        self.get_teams_func = func

    def register_export_clicked(self, func):
        self.export_func = func

    def export_teams(self, func):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Export file', 'teams.html')
        if name:
            self.export_func(name, self.round_id)


