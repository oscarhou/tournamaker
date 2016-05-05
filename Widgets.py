from PyQt4 import QtGui
import SqlTypes
class PlayerInfoWidget(QtGui.QWidget):

    def __init__(self):
        super(PlayerInfoWidget, self).__init__()
        layout = QtGui.QFormLayout()
        # set up buttons and input
        self.first_name = QtGui.QLineEdit()
        self.last_name = QtGui.QLineEdit()
        self.nickname = QtGui.QLineEdit()
        self.phone = QtGui.QLineEdit()
        self.save_player_info_button = QtGui.QPushButton("Save Player Info")

        layout.addRow("First Name:", self.first_name)
        layout.addRow("Last Name:", self.last_name)
        layout.addRow("Nickname:", self.nickname)
        layout.addRow("Phone:", self.phone)
        layout.addRow("", self.save_player_info_button)
        self.setLayout(layout)

    def set_player_data(self, player):
        self.first_name.setText(player.first_name)
        self.last_name.setText(player.last_name)
        self.nickname.setText(player.nickname)
        self.phone.setText(player.phone)

    def register_save_click(self, func):
        self.save_player_info_button.clicked.connect(func)

    def get_form_data(self):
      return {'first_name' : str(self.first_name.text()),
              'last_name' : str(self.last_name.text()),
              'nickname' : str(self.nickname.text()),
              'phone' : str(self.phone.text())}

class TeamWinLossWidget(QtGui.QWidget):
    def __init__(self):
        super(TeamWinLossWidget, self).__init__()
        self.label = QtGui.QLabel()
        self.win_button = QtGui.QPushButton("Win")
        self.win_button.clicked.connect(self.win_click)
        self.lose_button = QtGui.QPushButton("Lose")
        self.lose_button.clicked.connect(self.lose_click)
        v_layout = QtGui.QVBoxLayout()
        v_layout.addWidget(self.label)
        h_layout = QtGui.QHBoxLayout()
        h_layout.addWidget(self.win_button)
        h_layout.addWidget(self.lose_button)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def set_opponent(self, opponent):
        self.label.setText("Result vs \n Team {}?".format(opponent))

    def register_win_lose_click(self, func):
        self.clicked_func = func

    def lose_click(self):
        self.clicked_func(False)

    def win_click(self):
        self.clicked_func(True)

