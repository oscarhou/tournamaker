from PyQt4 import QtGui
from model import GenericModel

class TournamentPlayerWidget(QtGui.QWidget):
    def __init__(self, model=None, parent=None, round_id=None):
        super(TournamentPlayerWidget, self).__init__()
        self.round_id=round_id
        self.enroll_handler_func = None

        players_tab_layout = QtGui.QGridLayout(self)
        # set up view widget
        self.player_list_view = QtGui.QTableView()
        self.player_list_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.player_list_view.horizontalHeader().setStretchLastSection(True)
        self.player_list_model = model
        self.player_list_view.setModel(self.player_list_model)

        self.enroll_player_button = QtGui.QPushButton("Enroll Players")
        self.enroll_player_button.clicked.connect(self.enroll_clicked)

        self.export_players_button = QtGui.QPushButton("Export Players")
        self.export_players_button.clicked.connect(self.export_players)

        players_tab_layout.addWidget(self.player_list_view)
        players_tab_layout.addWidget(self.enroll_player_button)
        players_tab_layout.addWidget(self.export_players_button)
        self.setLayout(players_tab_layout)
        self.show()

    def set_model(self, model):
        self.player_list_view.setModel(model)
        self.player_list_view.resizeColumnsToContents()

    def reload(self, data):
        self.player_list_model.reload(data)

    def register_enroll_player_clicked(self, func):
        self.enroll_handler_func = func

    def enroll_clicked(self):
        self.enroll_handler_func(self.round_id)

    def register_export_clicked(self, func):
        self.export_func = func

    def export_players(self, func):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Export file', 'export.txt')
        if name:
            self.export_func(name, self.round_id)
