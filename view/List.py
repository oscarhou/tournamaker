from PyQt4 import QtGui

class GenericListModel(QtGui.QStandardItemModel):
    def __init__(self, parentWidget):
        super(GenericListModel, self).__init__(parentWidget)
        self.parentWidget = parentWidget

    def add_items(self, list_of_items):
        for item in list_of_items:
            q_item= QtGui.QStandardItem()
            q_item.setText(item)
            q_item.setEditable(False)
            self.appendRow(q_item)