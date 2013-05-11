import copy
from PySide import QtGui

class BufRefImage(QtGui.QImage):
    """ Class that keeps a reference to the data buffer to prevent it from being garbage collected. 
    """
    def __init__(self, data, width, height, format):
        self._data = data
        super(BufRefImage, self).__init__(self._data, width, height, format)
        
        
class BufCopyImage(QtGui.QImage):
    """ Class that keeps a reference to the data buffer to prevent it from being garbage collected. 
    """
    def __init__(self, data, width, height, format):
        self._data = copy.deepcopy(data)
        super(BufCopyImage, self).__init__(self._data, width, height, format)
        
