from PyQt4 import QtGui, QtCore
from model import GenericModel
from TournamentPlayerWidget import TournamentPlayerWidget
from Widgets import TeamWinLossWidget
from CustomDialogs import ManageGroupDialog, MessageDialog
from TeamMaker import generate_teams, match_teams
import SqlTypes
import MatchHelpers
from my_utility import TournamentLoader


class TeamsWidget(QtGui.QWidget):
    def __init__(self, model=None, parent=None, round_id=None, is_first_round=True):
        super(TeamsWidget, self).__init__()

        self.teams_count = 0
        self.get_teams_func = None
        self.export_func = None
        self.manage_groups_button = None
        self.round_id = round_id
        self.is_first_round = is_first_round

        #teams model
        self.teams_model = GenericModel.TableModel(["Name", "Players", "Opponent", "Result", "W/L/B"])
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
        self.manage_groups_button = QtGui.QPushButton()
        if is_first_round:
            self.generate_teams_button.setText("Generate Teams")
            self.generate_teams_button.clicked.connect(self.generate_teams_or_error_dialog)
            self.manage_groups_button.setText("Manage Groups")
            self.manage_groups_button.clicked.connect(self.manage_groups_clicked)
        else:
            self.generate_teams_button.setText("Match Teams")
            self.generate_teams_button.clicked.connect(lambda: match_teams(self.round_id))
            self.manage_groups_button.setText("Manage Teams")
            self.manage_groups_button.clicked.connect(self.manage_groups_clicked)

        #button for creating teams
        self.export_teams_button = QtGui.QPushButton()
        self.export_teams_button.setText("Export")
        self.export_teams_button.clicked.connect(self.export_teams)

        # Forms
        self.team_win_loss_widget = TeamWinLossWidget()
        self.team_win_loss_widget.register_win_lose_click(self.team_win_loss_clicked)

        self.team_win_loss_handler_func = None

        teams_tab_layout = QtGui.QHBoxLayout()
        left_vert_layout = QtGui.QVBoxLayout()
        left_vert_layout.addWidget(self.players_widget)
        if self.manage_groups_button:
            left_vert_layout.addWidget(self.manage_groups_button)
        right_vert_layout = QtGui.QVBoxLayout()
        #add widgets to layout
        right_vert_layout.addWidget(self.teams_view)
        right_vert_layout.addWidget(self.team_win_loss_widget)
        right_vert_layout.addWidget(self.generate_teams_button)
        right_vert_layout.addWidget(self.export_teams_button)
        teams_tab_layout.addLayout(left_vert_layout)
        teams_tab_layout.addLayout(right_vert_layout)
        teams_tab_layout.setStretchFactor(right_vert_layout, 3)

        self.setLayout(teams_tab_layout)
        self.show()
    def generate_teams_or_error_dialog(self):
        try:
            generate_teams(self.round_id)
        except Exception as e:
            MessageDialog(self,
                "Error: {}".format(e),
                QtGui.QMessageBox.Ok).exec_()

    def disable_buttons(self):
        self.generate_teams_button.setEnabled(False)
        self.players_widget.disable()
        self.team_win_loss_widget.disable(True)
        self.manage_groups_button.setEnabled(False)

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

    def manage_groups_clicked(self):
        all_players = MatchHelpers.query_by_round_id(SqlTypes.Player, self.round_id).all()
        groups_list = None
        enrolled_players = []
        if self.is_first_round:
            groups_list = SqlTypes.session.query(SqlTypes.Group).filter(SqlTypes.Group.round_id==self.round_id).all()
            # only show players in the list that are in the round but do not have a team
            for player in all_players:
                found = False
                for group in player.groups:
                    if group.round_id == self.round_id:
                        found = True
                        break
                if not found:
                    enrolled_players.append(player)
        else:
            groups_list = SqlTypes.session.query(SqlTypes.Team).filter(SqlTypes.Team.rounds.any(id=self.round_id)).all()
            for player in all_players:
                found = False
                for team in player.teams:
                    # if player is on a team that exists in this round
                    if [ x for x in groups_list if x.id == team.id ]:
                        found = True
                        break
                if not found:
                    enrolled_players.append(player)
        ManageGroupDialog(self.is_first_round, self.round_id, groups_list, enrolled_players).exec_()

    def team_win_loss_clicked(self, team_won):
        team_id = self.teams_model.data(
            self.teams_view.selectedIndexes()[0], QtCore.Qt.UserRole)
        team = SqlTypes.session.query(SqlTypes.Team).filter(SqlTypes.Team.id==team_id).first()
        match = MatchHelpers.get_win_loss(team.id, self.round_id)

        this_team_win_loss= MatchHelpers.get_win_loss(team_id, self.round_id)
        opponent_team_win_loss= MatchHelpers.get_win_loss(match.opponent_id, self.round_id)

        if team_won:
            this_team_win_loss.win_loss = SqlTypes.WinLossEnum.Win
            opponent_team_win_loss.win_loss = SqlTypes.WinLossEnum.Lose
        else:
            this_team_win_loss.win_loss = SqlTypes.WinLossEnum.Lose
            opponent_team_win_loss.win_loss = SqlTypes.WinLossEnum.Win
        SqlTypes.session.commit()

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

    def export_teams(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Export file', 'teams.html')
        if name:
            current_teams = SqlTypes.sql_query(
                SqlTypes.Team,
                SqlTypes.Team.rounds.any(id=self.round_id)).all()
            this_round = SqlTypes.get_by_id(SqlTypes.Round, self.round_id)
            win_loss_dict = {}
            # get win loss records for the players
            for player in this_round.players:
                win,loss = MatchHelpers.get_player_win_loss(this_round.tournament_id, player.id)
                win_loss_dict[player.id] = { "player" : player, "win" : win, "loss" : loss}

            TournamentLoader.export_teams_to_file(name, current_teams, win_loss_dict)

