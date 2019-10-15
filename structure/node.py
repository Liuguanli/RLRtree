import numpy as np

class Node:
    def __init__(self, ):
        # self.mbr = []
        pass

    def __str__(self) -> str:
        str = "mbr[" + ",".join(self.mbr) + "]" + "\n"
        for item in self.nodes:
            str = str + item + "\n"
        return str

    # only for 2 dim
    # def interact(self, another_mbr):
    #     points = [[another_mbr[0], another_mbr[1]], [another_mbr[0], another_mbr[3]], [another_mbr[2], another_mbr[1]],
    #               [another_mbr[2], another_mbr[3]]]
    #
    #     dim = int(len(another_mbr) / 2)
    #
    #     for point in points:
    #         if self.mbr[0] <= point[0] <= self.mbr[0 + dim] and self.mbr[1] <= point[1] <= self.mbr[1 + dim]:
    #             return True
    #
    #     points = [[self.mbr[0], self.mbr[1]], [self.mbr[0], self.mbr[3]], [self.mbr[2], self.mbr[1]],
    #               [self.mbr[2], self.mbr[3]]]
    #
    #     for point in points:
    #         if another_mbr[0] <= point[0] <= another_mbr[0 + dim] and another_mbr[1] <= point[1] <= another_mbr[1 + dim]:
    #             return True
    #     return False
    #
    # def get_reward(self, mbr):
    #     return self.get_overlap(mbr)
    #
    # def get_overlap(self, mbr):
    #     retult = 0
    #     for node in self.nodes:
    #         overlap = 1.0
    #         # print(mbr, node.mbr, node.interact(mbr))
    #         if node.interact(mbr):
    #             dim = int(len(mbr) / 2)
    #             for index in range(dim):
    #                 overlap *= (max(node.mbr[index + dim], mbr[index + dim]) - min(node.mbr[index], mbr[index]))
    #             retult += overlap
    #     return retult
    #
    # def cal_area(self, mbr):
    #     cost = 1
    #     for i in range(self.dim):
    #         cost *= (mbr[i + self.dim] - mbr[i])
    #     return cost
    #
    # def cal_MBR(self, coordinates):
    #     mbr = []
    #     for index in range(self.dim):
    #         mbr.append(np.min(coordinates[index]))
    #     for index in range(self.dim):
    #         mbr.append(np.max(coordinates[index + self.dim]))
    #     return mbr
    #
    # def move_in(self, node, index=0):
    #     self.nodes.insert(index, node)
    #     self.update_mbr(node.mbr)
    #
    # def move_out(self, index=0):
    #     result = self.nodes.pop(index)
    #     return result
