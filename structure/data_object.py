from structure.node import Node


class data_object(Node):

    def __init__(self, location, order, index, dim, pagesize=100):
        super(data_object, self).__init__()
        self.location = location
        self.pagesize = pagesize
        self.index = index
        self.order = order
        self.mbr = location * dim
        self.parent = None

    def __str__(self) -> str:
        s = "mbr[" + ",".join(map(str, self.location)) + "]" + "\n"
        return str(self.index) + " " + str(self.order) + " " + s

    def get_levels(self, root):
        # return_str = str(self.parent.nodes.index(self))
        return_str = ''
        item = self.parent
        while item is not root:
            return_str += ',' + str(item.order)
            item = item.parent
        return return_str
