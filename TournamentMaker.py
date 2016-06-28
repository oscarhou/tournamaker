from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal
from functools import partial
from model import TournamentModel, GenericModel
from TeamTabWidget import TeamsWidget
from TournamentPlayerWidget import TournamentPlayerWidget
from my_utility import TournamentLoader
from Buttons import DialogButton, AddPlayerListButton, CreateTournamentButton
from CustomDialogs import AddPlayerDialog, EnrollPlayerDialog, MessageDialog, ManageGroupDialog
from Widgets import PlayerInfoWidget
from view.CreateGroupView import CreateGroup
import SqlTypes
import TeamMaker
import sys
import MatchHelpers
class TournaGUI(QtGui.QWidget):
    def __init__(self):
        super(TournaGUI, self).__init__()
        tournament = SqlTypes.session.query(SqlTypes.Tournament).first()
        self.selected_tournament = tournament
        self.tab_widget = None
        self.players_tab = None
        self.teams_tab = None
        self.current_player_list = []
        self.current_player_id = None
        self.current_tournament_name = None
        self.initialize_ui()
        self.initialize_tabs()
        self.initialize_layout()
        self.reload_all_player_list()
        self.current_rounds = []
        self.show()

    def initialize_ui(self):
        self.resize(1024, 724)
        self.move(300, 300)
        self.setWindowTitle('TournaMaker')

        self.layout = QtGui.QHBoxLayout()
#        self.layout.setSpacing(10)

        self.main_tab_widget = QtGui.QTabWidget(self)
        self.tournament_list_view = QtGui.QListView(self)
        self.tournament_list_model = GenericModel.Generic(self.tournament_list_view)
        self.tournament_list_view.setModel(self.tournament_list_model)

        # register slot for when a tournament is clicked
        self.tournament_list_view.clicked.connect(self.clicked_tournament)
        self.reload_tournament_list()

        self.add_player_btn = QtGui.QPushButton("Add Player")
        self.add_player_btn.clicked.connect(self.add_player)
        self.add_player_btn.setEnabled(True)

        self.add_player_list_btn = AddPlayerListButton(self)
        self.add_player_list_btn.register_handler_func(self.load_csv_file)

        self.create_tournament_btn = CreateTournamentButton(self)
        self.create_tournament_btn.register_handler_func(self.add_new_tournament)

        self.delete_tournament_btn = QtGui.QPushButton("Delete Tournament")
        self.delete_tournament_btn.clicked.connect(self.delete_tournament)

        # shows all players added to the app
        self.all_player_list_view = QtGui.QListView(self)
        self.all_player_list_model = GenericModel.Generic(self.all_player_list_view)
        self.all_player_list_view.setModel(self.all_player_list_model)
        self.all_player_list_view.clicked.connect(self.clicked_all_player_item)

        # shows player info
        self.player_info = PlayerInfoWidget()
        self.player_info.register_save_click(self.update_player_info)

        # self create new round
        self.add_round_btn = QtGui.QPushButton("Add Round")
        self.add_round_btn.clicked.connect(self.add_new_round_to_selected_tournament)

    def update_player_info(self):
        player = SqlTypes.session.query(SqlTypes.Player).filter(SqlTypes.Player.id == self.current_player_id).first()
        data_dict = self.player_info.get_form_data()
        if (SqlTypes.nickname_exists(data_dict["nickname"])
            and data_dict["nickname"] != player.nickname):
            MessageDialog(self,
                "Name already {} exists".format(data_dict["nickname"]),
                QtGui.QMessageBox.Ok)
        else:
            player.first_name = data_dict["first_name"]
            player.last_name = data_dict["last_name"]
            player.nickname = data_dict["nickname"]
            player.phone = data_dict["phone"]
            SqlTypes.session.commit()
            self.reload_all_player_list()

    def add_player(self, player):
        playerButton = AddPlayerDialog(self)
        # open dialog and get data if ok pressed
        if (playerButton.exec_()):
            data = playerButton.get_form_data()
            new_player = SqlTypes.Player(
                first_name=data['first_name'],
                last_name=data['last_name'],
                nickname=data['nickname'],
                phone=data['phone'])

            # commit to database
            if (SqlTypes.add_player_to_db(new_player)):
                SqlTypes.session.commit()
                self.reload_all_player_list()
            else:
                MessageDialog(self,
                              "Name already {} exists".format(new_player.nickname),
                              QtGui.QMessageBox.Ok).exec_()

    def clicked_tournament(self, model_index):
        tournament_name = str(self.tournament_list_model.itemFromIndex(model_index).text())
        self.selected_tournament = \
            SqlTypes.session.query(SqlTypes.Tournament).filter(
                SqlTypes.Tournament.name == tournament_name).first()
        self.show_rounds()
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        round_id = self.tab_widget.currentWidget().round_id
        self.reload_player_list(round_id)
        self.reload_teams(round_id)

    def clicked_all_player_item(self, model_index):
        item = self.all_player_list_model.itemFromIndex(model_index)
        data = item.data(QtCore.Qt.UserRole).toPyObject()
        self.current_player_id = data
        self.player_info.set_player_data(
            SqlTypes.session.query(SqlTypes.Player).filter(SqlTypes.Player.id == data).first())
        MatchHelpers.get_player_win_loss(self.selected_tournament.id, self.current_player_id)

    def initialize_tabs(self):
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.currentChanged.connect(self.reload_current_round_tab)
        self.show_rounds()
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def reload_current_round_tab(self):
        round_id = self.tab_widget.currentWidget().round_id
        self.reload_player_list(round_id)
        self.reload_teams(round_id)

    def show_rounds(self):
        if self.selected_tournament:
            self.current_rounds = []
            self.tab_widget.clear()
            rounds = SqlTypes.session.query(SqlTypes.Round).filter(SqlTypes.Round.tournament_id==self.selected_tournament.id).all()

            for index, round_item in enumerate(sorted(rounds, key=lambda item: item.round_count)):
                this_round = self.setup_round_tab(round_item.id, index == 0)
                if index < len(rounds) - 1:
                    this_round.disable_buttons()

                self.current_rounds.append(this_round)
                self.tab_widget.addTab(this_round, "Round {}".format(round_item.round_count))

    # creates a round instance and sets up the callbacks WHICH SUCK
    def setup_round_tab(self,round_id, is_first_round):
        round_tab = TeamsWidget(round_id=round_id, is_first_round=is_first_round)
        round_tab.register_export_clicked(self.export_team_data)
        round_tab.register_enroll_player_clicked(self.enroll_players)
        round_tab.register_player_export_clicked(self.export_players)
        return round_tab

    # apply SQL changes after enrolling/unenrolling players to a tournament
    def enroll_players(self, round_id):
        enroll_dialog = EnrollPlayerDialog(
            SqlTypes.session.query(SqlTypes.Player).filter(~SqlTypes.Player.rounds.any(SqlTypes.Round.id == round_id)).all(),
            SqlTypes.session.query(SqlTypes.Player).filter(SqlTypes.Player.rounds.any(SqlTypes.Round.id == round_id)).all())
        if (enroll_dialog.exec_()):
            enrolled, non_enrolled = enroll_dialog.get_lists()

            this_round = SqlTypes.session.query(SqlTypes.Round).filter(SqlTypes.Round.id==round_id).first()

            # move Player to enrolled
            for enrolled_id in enrolled:
                enrolled_player = SqlTypes.session.query(SqlTypes.Player).get(enrolled_id)
                # if enrolled player does not have tournament then add it
                if (not self.check_has_id(round_id, enrolled_player.rounds)):
                    enrolled_player.rounds.append(this_round)

            # move Player to non enrolled 
            for non_enrolled_id in non_enrolled:
                non_enrolled_player = SqlTypes.session.query(SqlTypes.Player).get(non_enrolled_id)
                # if non_enrolled player has the tournament then remove it
                if (self.check_has_id(round_id, non_enrolled_player.rounds)):
                    non_enrolled_player.rounds.remove(this_round)

            # commit changes
            SqlTypes.session.commit()

        self.reload_player_list(round_id)

    def check_has_id(self, check_id, object_list):
        found = False
        for player_tournament in object_list:
            if player_tournament.id == check_id:
                found = True
                break

        return found

    def initialize_layout(self):
        vert_layout_left = QtGui.QVBoxLayout()
        vert_layout_left.addWidget(self.add_player_btn)
        vert_layout_left.addWidget(self.add_player_list_btn)
        vert_layout_left.addWidget(self.all_player_list_view)
        vert_layout_left.addWidget(self.player_info)
        vert_layout_right = QtGui.QVBoxLayout()
        hor_layout_right = QtGui.QHBoxLayout()
        hor_layout_right.addWidget(self.create_tournament_btn)
        hor_layout_right.addWidget(self.delete_tournament_btn)
        vert_layout_right.addLayout(hor_layout_right)
        vert_layout_right.addWidget(self.tournament_list_view)
        vert_layout_right.addWidget(self.add_round_btn)
        vert_layout_right.addWidget(self.tab_widget)
        vert_layout_right.setStretchFactor(self.tab_widget, 10)
        self.layout.addLayout(vert_layout_left)
        self.layout.addLayout(vert_layout_right)

        self.layout.setStretchFactor(vert_layout_right, 3)

        self.setLayout(self.layout)

    def get_round_tab(self, this_round_id):
        for count in xrange(0, self.tab_widget.count()):
            widget = self.tab_widget.widget(count)
            if widget.round_id == this_round_id:
                return widget

    # reloads the tournament specific lists
    def reload_player_list(self, round_id):
        this_round = SqlTypes.get_by_id(SqlTypes.Round, round_id)
        players = SqlTypes.session.query(SqlTypes.Player.nickname) \
            .filter(SqlTypes.Player.rounds.any(id=round_id)).all()
        self.get_round_tab(round_id).players_reload(players)

    # reloads the total player list
    def reload_all_player_list(self):
        self.all_player_list_model.reload(
            SqlTypes.session.query(SqlTypes.Player.id, SqlTypes.Player.nickname).all())

    def reload_tournament_list(self):
        self.tournament_list_model.reload(
            SqlTypes.session.query(SqlTypes.Tournament.id, SqlTypes.Tournament.name).all())
        #choose the first item in the remaining list
        index = self.tournament_list_model.index(0,0)

        # if an index was found aka if we still have items in the list
        if index:
            #set the item as selected
            self.tournament_list_view.setCurrentIndex(index)

            #set the current selected item
            item = self.tournament_list_model.itemFromIndex(index)
            data = item.data(QtCore.Qt.UserRole).toPyObject()
            self.selected_tournament = SqlTypes.session.query(SqlTypes.Tournament).get(data)

    def reload_teams(self, this_round_id):
        # clear old model data and grab updated data from tournament
        data_rows = []
        id_rows = []
        current_round = SqlTypes.session.query(SqlTypes.Round).filter(SqlTypes.Round.id==this_round_id).first()
        tournament_rounds = SqlTypes.get_rounds_by_tournament_id(current_round.tournament_id)
        # clear existing teams
        current_teams = current_round.teams

        for team in current_teams:
            team_list_string = ""

            # get win/loss result of current round match-up
            team_round = MatchHelpers.get_win_loss(team.id, this_round_id)
            opponent_name = ""
            if (team_round.opponent_id):
                opponent = SqlTypes.session.query(SqlTypes.Team).filter(SqlTypes.Team.id==team_round.opponent_id).first()
                opponent_name = opponent.name

            win_loss_str = "N/A"
            if team_round.win_loss == SqlTypes.WinLossEnum.Win:
                win_loss_str = "Win"
            elif team_round.win_loss == SqlTypes.WinLossEnum.Lose:
                win_loss_str = "Lose"

            # make the team list string
            for member in team.players:
                if team_list_string:
                    team_list_string += ","

                team_list_string += member.nickname

            # get total stats up until now
            wins = 0
            losses = 0
            byes = 0
            for this_round in tournament_rounds:
                if this_round.round_count > current_round.round_count:
                    continue

                this_match = MatchHelpers.get_win_loss(team.id, this_round.id)
                if this_match.win_loss == SqlTypes.WinLossEnum.Win:
                    wins += 1
                elif this_match.win_loss == SqlTypes.WinLossEnum.Lose:
                    losses += 1
                elif this_match.win_loss == SqlTypes.WinLossEnum.NotPlayed:
                    byes += 1

            data_rows.append([team.name, team_list_string, opponent_name, win_loss_str, "{}/{}/{}".format(wins, losses, byes)])
            id_rows.append(team.id)

        self.get_round_tab(this_round_id).teams_reload(id_rows, data_rows)


    def export_team_data(self, location, round_id):
        current_teams = SqlTypes.sql_query(
            SqlTypes.Team,
            SqlTypes.Team.rounds.any(id=round_id)).all()
        this_round = SqlTypes.get_by_id(SqlTypes.Round, round_id)
        win_loss_dict = {}
        # get win loss records for the players
        for player in this_round.players:
            win,loss = SqlTypes.get_player_win_loss(this_round.tournament_id, player.id)
            win_loss_dict[player.id] = { "player" : player, "win" : win, "loss" : loss}

        TournamentLoader.export_teams_to_file(location, current_teams, win_loss_dict)

    def export_players(self, location, round_id):
        current_teams = SqlTypes.sql_query(
            SqlTypes.Player.nickname,
            SqlTypes.Player.rounds.any(id=round_id)).all()

        TournamentLoader.export_players_to_file(location, current_teams)

    def load_csv_file(self, filename):
        import csv
        players_not_added = []
        with open(filename, 'rb') as csvfile:
            csvdata = csv.reader(csvfile)
            # add each player
            for row in csvdata:
                this_phone = ""
                # if we see and invalid row just return
                if len(row) < 3:
                    MessageDialog(self,
                        "Invalid CSV too few columns: {}".format(row),
                        QtGui.QMessageBox.Ok).exec_()
                    # don't add any changes
                    SqlTypes.session.rollback()
                    return
                elif len(row) > 3:
                    this_phone = row[3]

                player = SqlTypes.Player(
                    nickname=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    phone=this_phone)

                # make note of the player that was not added
                if (not SqlTypes.add_player_to_db(player)):
                    players_not_added.append(player.nickname)

            # commit after all players have been parsed
            SqlTypes.session.commit()

        # refresh view
        self.reload_all_player_list()

        # show error
        if len(players_not_added):
            name_string = ""
            for player in players_not_added:
                name_string += "{}\n".format(player)

            MessageDialog(self,
                "Names not added (duplicates): \n{}".format(name_string),
                QtGui.QMessageBox.Ok).exec_()

    def add_new_tournament(self, tournament_name):
        # add if tournament does not exist already
        if not SqlTypes.session.query(SqlTypes.Tournament).filter(SqlTypes.Tournament.name==tournament_name).first():
            tournament = SqlTypes.Tournament(name=tournament_name)
            SqlTypes.session.add(tournament)
            SqlTypes.session.commit()
            self.reload_tournament_list()

            # create a round for this tournament
            SqlTypes.add_new_round(tournament.id)

    def delete_tournament(self):
        #delete the item from the list
        box = MessageDialog(self, "Are you sure you want to delete this tournament?", QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        if box.exec_() == QtGui.QMessageBox.Ok:
            SqlTypes.session.delete(self.selected_tournament)
            SqlTypes.session.commit()
            self.reload_tournament_list()

    def add_new_round_to_selected_tournament(self):
        round_latest = max(SqlTypes.get_rounds_by_tournament_id(self.selected_tournament.id), key= lambda x: x.round_count)
        current_round_matches = SqlTypes.get_team_rounds_by_round_id(round_latest.id)
        unplayed_matches = 0
        for match in current_round_matches:
            if match.win_loss == SqlTypes.WinLossEnum.NotPlayed:
                unplayed_matches += 1

            if unplayed_matches > 1:
                MessageDialog(self, "Match results not updated", QtGui.QMessageBox.Ok).exec_()
                return

        SqlTypes.add_new_round(self.selected_tournament.id)

def main():
    app = QtGui.QApplication(sys.argv)
    gui = TournaGUI()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
