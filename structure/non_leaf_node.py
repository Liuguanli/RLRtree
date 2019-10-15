import copy

from structure.node import Node
import numpy as np
import sys

ACTION_LEFT = -1
ACTION_RIGHT = 1


class NonLeafNode(Node):

    def __init__(self, dim, pagesize, order):
        super(NonLeafNode, self).__init__()
        self.order = order
        self.mbr = []
        self.pagesize = pagesize
        self.nodes = []
        self.dim = dim
        self.parent = None
        # self.original_page_size = []
        # self.level_one_node_sizes = []

    def add(self, node):
        self.nodes.append(node)
        self.update_mbr(node.mbr)
        # if self.parent is not None:
        #     self.parent.update_mbr(self.mbr)

    def update_mbr(self, location):
        locations = copy.deepcopy(location)
        if self.mbr is None or len(self.mbr) == 0:
            self.mbr = locations
            # print('non leaf', locations)
        else:
            length = int(len(locations) / 2)
            for i in range(length):
                if locations[i] < self.mbr[i]:
                    self.mbr[i] = locations[i]
                if locations[i + length] > self.mbr[i + length]:
                    self.mbr[i + length] = locations[i + length]
            # print('non leaf else', self.mbr)

    # def remove_from_mbr(self, location):

    def update(self):
        for item in self.nodes:
            self.update_mbr(item.mbr)

    def __str__(self) -> str:
        return str(self.order)

    # --------------moving-------------------

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
    #
    # def get_total_area(self):
    #     total_area = 0
    #     for child in self.nodes:
    #         coordinates = child.get_coordinates()
    #         total_area += self.cal_area(self.cal_MBR(coordinates))
    #     return total_area

    def step_move(self, observation, action, strategy='radical'):
        left_node = self.nodes[action]
        right_node = self.nodes[action + 1]

        move_right_able = False
        move_left_able = False
        if len(left_node.nodes) > self.pagesize / 2 and len(right_node.nodes) < self.pagesize:
            move_left_able = True
        if len(right_node.nodes) > self.pagesize / 2 and len(left_node.nodes) < self.pagesize:
            move_right_able = True

        # print('left_node', left_node.get_coordinates())
        # print('right_node', right_node.get_coordinates())
        left_node_coordinates = left_node.get_coordinates()
        right_node_coordinates = right_node.get_coordinates()
        # not move
        not_move_area = self.get_reward(self.cal_MBR(left_node_coordinates)) + self.get_reward(
            self.cal_MBR(right_node_coordinates))

        # print("not_move_area", not_move_area)

        move_left_area = sys.float_info.max
        move_right_area = sys.float_info.max

        # move left
        if move_left_able:
            left = np.array(left_node_coordinates)[:, 0:-1]
            temp = np.array(left_node_coordinates)[:, -1].reshape(self.dim * 2, 1)
            right = np.array(right_node_coordinates)
            right = np.hstack((temp, right))
            mbr_left_move_left = self.cal_MBR(left)  # after moving out, re-cal the Mbr
            mbr_right_move_left = self.cal_MBR(right)
            move_left_area = self.get_reward(mbr_left_move_left) + self.get_reward(mbr_right_move_left)
            # print("move_left_area", move_left_area)

        # move right
        if move_right_able:
            right = np.array(right_node_coordinates)[:, 1:]
            temp = np.array(right_node_coordinates)[:, 0].reshape(self.dim * 2, 1)
            left = np.array(left_node_coordinates)
            left = np.hstack((left, temp))
            mbr_left_move_right = self.cal_MBR(left)  # after moving out, re-cal the Mbr
            mbr_right_move_right = self.cal_MBR(right)
            move_right_area = self.get_reward(mbr_left_move_right) + self.get_reward(mbr_right_move_right)
            # print("move_right_area", move_right_area)

        # TODO if changed parent and other parameters should be changed

        reward = 0
        move_action = 0

        if strategy == 'radical':
            # this is a trial
            if move_left_area < move_right_area:
                if move_left_able:
                    move_action = ACTION_LEFT
                    reward = not_move_area - move_left_area
            else:
                if move_right_able:
                    move_action = ACTION_RIGHT
                    reward = not_move_area - move_right_area
        else:
            if move_left_area < not_move_area:
                reward = not_move_area - move_left_area
                move_action = -1

            if move_right_area < not_move_area:
                if reward < (not_move_area - move_right_area):
                    reward = not_move_area - move_right_area
                    move_action = 1

        # print('reward', reward)
        #
        # print('not_move_area', not_move_area, 'move_left_area', move_left_area, 'move_right_area', move_right_area,
        #       'move_action', move_action)
        # print('total_area before', self.get_total_area())

        if move_action == ACTION_LEFT:
            temp = left_node.move_out(len(left_node.nodes) - 1)
            left_node.mbr = mbr_left_move_left
            temp.parent = right_node
            right_node.move_in(temp)
        if move_action == ACTION_RIGHT:
            temp = right_node.move_out()
            right_node.mbr = mbr_right_move_right
            temp.parent = left_node
            left_node.move_in(temp, len(left_node.nodes))

        # print('total_area after', self.get_total_area())
        done = False
        observation[action] += move_action

        # print('action', action, 'move_action', move_action, 'reward', reward)
        return observation, reward, done

    def update_mbr_after_move_out(self):
        self.mbr = None
        for item in self.nodes:
            self.update_mbr(item.mbr)

    def interact(self, another_mbr):
        points = [[another_mbr[0], another_mbr[1]], [another_mbr[0], another_mbr[3]], [another_mbr[2], another_mbr[1]],
                  [another_mbr[2], another_mbr[3]]]

        dim = int(len(another_mbr) / 2)

        for point in points:
            if self.mbr[0] <= point[0] <= self.mbr[0 + dim] and self.mbr[1] <= point[1] <= self.mbr[1 + dim]:
                return True

        points = [[self.mbr[0], self.mbr[1]], [self.mbr[0], self.mbr[3]], [self.mbr[2], self.mbr[1]],
                  [self.mbr[2], self.mbr[3]]]

        for point in points:
            if another_mbr[0] <= point[0] <= another_mbr[0 + dim] and another_mbr[1] <= point[1] <= another_mbr[
                1 + dim]:
                return True
        return False

    def get_reward(self, mbr):
        return self.get_overlap(mbr)

    def get_overlap(self, mbr):
        retult = 0
        for node in self.nodes:
            overlap = 1.0
            # print(mbr, node.mbr, node.interact(mbr))
            if node.interact(mbr):
                dim = int(len(mbr) / 2)
                for index in range(dim):
                    overlap *= (max(node.mbr[index + dim], mbr[index + dim]) - min(node.mbr[index], mbr[index]))
                retult += overlap
        return retult

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
        self.update_mbr(node.mbr)

    def move_out(self, index=0):
        result = self.nodes.pop(index)
        return result

    def step_exchange(self, observation, action):
        pass


