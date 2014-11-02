class Node(object):
    def __init__(self, data, column):
        self.up = self
        self.right = self
        self.down = self
        self.left = self

        self.data = data
        self.column = column

    def hasData(self):
        return self.data is not None

    def setUp(self, Node):
        self.up = Node
        Node.down = self

    def setRight(self, Node):
        self.right = Node
        Node.left = self

    def setDown(self, Node):
        self.down = Node
        Node.up = self

    def setLeft(self, Node):
        self.left = Node
        Node.right = self

    def rowNeighbours(self):
        firstNeighbour = self.right
        if firstNeighbour == self:
            return

        nextNeighbour = firstNeighbour
        while nextNeighbour != self:
            yield nextNeighbour
            nextNeighbour = nextNeighbour.right

    def reverseRowNeighbours(self):
        lastNeighbour = self.left
        if lastNeighbour == self:
            return

        nextNeighbour = lastNeighbour
        while nextNeighbour != self:
            yield nextNeighbour
            nextNeighbour = nextNeighbour.left

class HeadNode(Node):
    def __init__(self):
        super(HeadNode, self).__init__(None, None)
        self.setRight(self)

    def setUp(self, Node):
        return

    def setDown(self, Node):
        return

class ColumnNode(Node):
    def __init__(self, info):
        super(ColumnNode, self).__init__(None, self)

        self.size = 0
        self.info = info

        self.setUp(self)

    def addData(self, data):
        newNode = Node(data, self)

        lastNode = self.lastNode()

        self.setUp(newNode)
        newNode.setUp(lastNode)

        self.size += 1

    def firstNode(self):
        return self.down

    def lastNode(self):
        return self.up

    def nodes(self):
        firstNode = self.firstNode()
        if firstNode == self:
            return

        nextNode = firstNode
        while nextNode != self:
            yield nextNode
            nextNode = nextNode.down

    def nodesReverse(self):
        lastNode = self.lastNode()
        if lastNode == self:
            return

        nextNode = lastNode
        while nextNode != self:
            yield nextNode
            nextNode = nextNode.up

class toroidalLinkedList(object):
    def __init__(self):
        self.head = HeadNode()
        self.size = 0

    def addColumn(self, info):
        newColumn = ColumnNode(info)

        lastColumn = self.lastColumn()

        self.head.setLeft(newColumn)
        newColumn.setLeft(lastColumn)

        self.size += 1

    def columns(self):
        firstColumn = self.firstColumn()
        if firstColumn == self.head:
            return

        nextColumn = firstColumn
        while nextColumn != self.head:
            yield nextColumn
            nextColumn = nextColumn.right

    def firstColumn(self):
        return self.head.right

    def lastColumn(self):
        return self.head.left

    def smallestColumn(self):
        smallestColumn = self.firstColumn()
        smallestSize = smallestColumn.size
        for column in self.columns():
            if column.size < smallestSize:
                smallestSize = column.size
                smallestColumn = column
        return smallestColumn

    def cover(self, Column):
        Column.left.setRight(Column.right)

        for node in Column.nodes():
            for rowNeighbour in node.rowNeighbours():
                rowNeighbour.up.setDown(rowNeighbour.down)
                rowNeighbour.column.size -= 1

        self.size -= 1

    def uncover(self, Column):
        for node in Column.nodes():
            for rowNeighbour in node.rowNeighbours():
                rowNeighbour.up.setDown(rowNeighbour)
                rowNeighbour.column.size += 1

        Column.left.setRight(Column)

        self.size += 1

    def valid(self):
        for column in self.columns():
            if column.size == 0:
                return False

        return True

    def complete(self):
        return self.size == 0

if __name__ == "__main__":
    pass
