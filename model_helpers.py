from PyQt4 import QtCore
def get_id_list(model):
    id_list = []
    for index in range(model.rowCount()):
        item = model.item(index)
        # Get the object id from the UserRole field
        id_list.append(item.data(QtCore.Qt.UserRole).toPyObject())
    return id_list

