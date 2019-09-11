import copy

from structure.node import Node
import numpy as np
import sys

class LeafNode(Node):
    def __init__(self, dim, pagesize, order):
        super(LeafNode, self).__init__()
        self.order = order
        self.mbr = []
        self.pagesize = pagesize
        self.nodes = []
        self.dim = dim
        self.parent = None

    def add(self, data_object):
        self.nodes.append(data_object)
        self.update_mbr(data_object.location)
        # if self.parent is not None:
        #     self.parent.update_mbr(self.mbr)

    def update_mbr(self, location):
        locations = copy.deepcopy(location)
        if self.mbr is None or len(self.mbr) == 0:
            self.mbr = locations * self.dim
            # print('leaf', locations)
        else:
            length = len(locations)
            for i in range(length):
                if locations[i] < self.mbr[i]:
                    self.mbr[i] = locations[i]
                elif locations[i] > self.mbr[i + length]:
                    self.mbr[i + length] = locations[i]
            # print('leaf else', self.mbr)

    def update(self):
        for item in self.nodes:
            self.update_mbr(item.location)

    def get_coordinates(self):
        coordinates = [[] for i in range(self.dim * 2)]
        for i in range(len(self.nodes)):
            item = self.nodes[i].mbr
            for index in range(self.dim * 2):
                coordinates[index].append(item[index])
        # print('coordinates', coordinates)
        return coordinates

    def reset(self):
        level_one_node_sizes = []
        original_page_size = []
        for item in self.nodes:
            level_one_node_sizes.append(len(item.nodes))
            original_page_size.append(len(item.nodes))

        # print(level_one_node_sizes)
        # print(initial_state)
        # self.original_page_size = original_page_size
        # self.level_one_node_sizes = level_one_node_sizes
        return np.zeros(len(level_one_node_sizes) - 1), original_page_size

    def get_actions(self, level=0):
        return len(self.all_nodes[level]) - 1

    def step_move(self, observation, action):
        left_node = self.nodes[action]
        right_node = self.nodes[action + 1]

        move_right_able = False
        move_left_able = False
        if len(left_node.nodes) < self.pagesize and len(right_node.nodes) > self.pagesize / 2:
            move_left_able = True
        if len(right_node.nodes) < self.pagesize and len(left_node.nodes) > self.pagesize / 2:
            move_right_able = True

        # print('left_node', left_node.get_coordinates())
        # print('right_node', right_node.get_coordinates())
        left_node_coordinates = left_node.get_coordinates()
        right_node_coordinates = right_node.get_coordinates()
        # not move
        not_move_area = self.cal_area(self.cal_MBR(left_node_coordinates)) + self.cal_area(
            self.cal_MBR(right_node_coordinates))

        move_left_area = sys.float_info.max
        move_right_area = sys.float_info.max

        mbr_left = None
        mbr_right = None
        # move left
        if move_left_able:
            left = np.array(left_node_coordinates)[:, 0:-1]
            temp = np.array(left_node_coordinates)[:, -1].reshape(self.dim * 2, 1)
            right = np.array(right_node_coordinates)
            right = np.hstack((temp, right))
            # print('cal_MBR', self.cal_MBR(left))
            # print('cal_MBR', self.cal_MBR(right))
            move_left_area = self.cal_area(self.cal_MBR(left)) + self.cal_area(self.cal_MBR(right))
            mbr_left = self.cal_MBR(left)  # after moving out, re-cal the Mbr

        # move right
        if move_right_able:
            right = np.array(right_node_coordinates)[:, 1:]
            temp = np.array(right_node_coordinates)[:, 0].reshape(self.dim * 2, 1)
            left = np.array(left_node_coordinates)
            left = np.hstack((left, temp))
            # print('cal_MBR', self.cal_MBR(left))
            # print('cal_MBR', self.cal_MBR(right))
            move_right_area = self.cal_area(self.cal_MBR(left)) + self.cal_area(self.cal_MBR(right))
            mbr_right = self.cal_MBR(right)  # after moving out, re-cal the Mbr

        # TODO if changed parent and other parameters should be changed

        reward = 0
        move_action = 0
        if move_left_area < not_move_area:
            reward = not_move_area - move_left_area
            move_action = -1

        if move_right_area < not_move_area:
            if reward < (not_move_area - move_right_area):
                reward = not_move_area - move_right_area
                move_action = 1

        if move_action == -1:
            temp = right_node.move_out()
            right_node.mbr = mbr_right
            temp.parent = left_node
            left_node.move_in(temp, len(left_node.nodes))

        if move_action == 1:
            temp = left_node.move_out(len(left_node.nodes) - 1)
            left_node.mbr = mbr_left
            temp.parent = right_node
            right_node.move_in(temp)

        done = False
        observation[action] += move_action

        # print('action', action, 'move_action', move_action, 'reward', reward)
        return observation, reward, done

    def cal_area(self, mbr):
        cost = 1
        for i in range(self.dim):
            cost *= (mbr[i + self.dim] - mbr[i])
        return cost

    def cal_MBR(self, coordinates):
        mbr = []
        for index in range(self.dim):
            mbr.append(np.min(coordinates[index]))
        for index in range(self.dim):
            mbr.append(np.max(coordinates[index + self.dim]))
        return mbr

    def move_in(self, node, index=0):
        self.nodes.insert(index, node)
        self.update_mbr(node.location)

    def move_out(self, index=0):
        result = self.nodes.pop(index)
        return result

    def __str__(self) -> str:
        return str(self.order)
