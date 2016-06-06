from PyQt4 import QtGui, QtCore

class Generic(QtGui.QStandardItemModel):
    def __init__(self, parentWidget):
        super(Generic, self).__init__(parentWidget)
        self.parentWidget = parentWidget

    def add_items(self, list_of_items):
        for (item_id, item) in list_of_items:
            q_item= QtGui.QStandardItem()

            # set the displayed text
            q_item.setText(item)

            # store db_id of entry as hidden date to be retrieved later
            q_item.setData(item_id, QtCore.Qt.UserRole)
            q_item.setEditable(False)
            self.appendRow(q_item)

    def reload(self, id_text_tuple_list):
        self.clear()
        self.add_items(id_text_tuple_list)

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers):
        super(TableModel, self).__init__()
        self.array_dict = \
            {
                QtCore.Qt.DisplayRole : [],
                QtCore.Qt.UserRole : []
            }

        self.header_labels = headers

    def rowCount(self, parent):
        return len(self.array_dict[QtCore.Qt.DisplayRole])

    def columnCount(self, parent):
        if len(self.array_dict[QtCore.Qt.DisplayRole]):
            return len(self.array_dict[QtCore.Qt.DisplayRole][0])

        return 0

    def clear(self):
        self.array_dict = \
            {
                QtCore.Qt.DisplayRole : [],
                QtCore.Qt.UserRole : []
            }

    def reload(self, rows, role=QtCore.Qt.DisplayRole):
        self.clear()
        for row in rows:
            self.add_row(row, role)

    def setData(self, rows, role=QtCore.Qt.DisplayRole):
        self.array_dict[role] = rows
        self.layoutChanged.emit()

    def setRow(self, rowIndex, value, role=QtCore.Qt.DisplayRole):
        self.array_dict[role][rowIndex] = value
        self.layoutChanged.emit()

    def add_row(self, row, role=QtCore.Qt.DisplayRole):
        self.array_dict[role].append(row)
        self.layoutChanged.emit()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.UserRole:
            return QtCore.QVariant()

        return_value = QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return_value = self.array_dict[role][index.row()][index.column()]
        elif role == QtCore.Qt.UserRole:
            return_value = self.array_dict[role][index.row()]

        return return_value

    def getRow(self, index, role=QtCore.Qt.DisplayRole):
        if (role != QtCore.Qt.DisplayRole):
            return QtCore.QVariant()

        return self.array_dict[role][index.row()]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)


