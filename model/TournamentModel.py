from PyQt4 import QtGui

class Model(QtGui.QStandardItemModel):
    def __init__(self):
        super(Model, self).__init__()

    def add_items(self, tournaments):
        for tournament in tournaments:
            q_item = QtGui.QStandardItem()
            q_item.setText(tournament.name)
            q_item.setEditable(False)
            self.appendRow(q_item)


