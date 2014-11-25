from unittest import TestCase
from toroidalLinkedList import toroidalLinkedList


def setupFourColumns():
    newList = toroidalLinkedList()
    for info in ("A", "B", "C", "D"):
        newList.addColumn(info)
    return newList


def setupFourColumnsWithData():
    newList = setupFourColumns()
    for i, column in enumerate(newList.columns()):
        for j in xrange(1, 4):
            column.addData(i * 3 + j)
    return newList


def setupListWithRows():
    newList = setupFourColumnsWithData()
    links = (1, 4), (5, 8), (9, 12)
    for link in links:
        for column in newList.columns():
            for node in column.nodes():
                for column2 in newList.columns():
                    for node2 in column2.nodes():
                        if node.data == link[0] and node2.data == link[1]:
                            node.setRight(node2)
                            node.setLeft(node2)
    return newList


class TestToroidalLinkedList(TestCase):
    def test_AddColumn(self):
        newList = toroidalLinkedList()
        newList.addColumn("A")
        self.assertEquals(newList.head.right.info, "A")


    def test_AddNodeToColumn(self):
        newList = setupFourColumns()
        newList.firstColumn().addData(1)
        self.assertEquals(newList.firstColumn().down.data, 1)
        self.assertEquals(newList.firstColumn().size, 1)


    def test_Cover(self):
        newList = setupListWithRows()
        for column in newList.columns():
            if column.info == "B":
                columnB = column

        newList.cover(columnB)

        contents = []
        for column in newList.columns():
            for node in column.nodes():
                contents.append(node.data)

        self.assertEquals(contents, [2, 3, 7, 9, 10, 11, 12])


    def test_Uncover(self):
        newList = setupListWithRows()
        for column in newList.columns():
            if column.info == "B":
                columnB = column

        newList.cover(columnB)
        newList.uncover(columnB)

        contents = []
        for column in newList.columns():
            for node in column.nodes():
                contents.append(node.data)

        self.assertEquals(contents, range(1,13))