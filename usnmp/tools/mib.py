import usnmp

class node:
    def __init__(self, parent=None, data=None):
        self.parent = parent
        self.children = []
        self.data = data
