import sys, getopt
import os
import numpy as np

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from algorithms.DDPG.brain import DeepDeterministicPolicyGradient
from algorithms.random.random import random_algorithm
from algorithms.DQN.brain import DeepQNetwork
from structure.data_object import data_object
from structure.leaf_node import LeafNode
from structure.non_leaf_node import NonLeafNode

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed

import logging

logging.getLogger('tensorflow').disabled = True  # this works to disable the WARNINGS

class Rtree:
    def __init__(self, file, dim, level, pagesize=100, output_file=None):
        self.root = None
        self.file = file
        self.dim = dim
        self.level = level
        self.pagesize = pagesize
        self.output_file = output_file

    def build_rtree(self):
        # to store all nodes in each level
        self.all_nodes = [[] for i in range(self.level)]
        with open(self.file, "r") as f:
            order = 0
            before = [0] * self.level
            temp = LeafNode(self.dim, self.pagesize, 0)
            nodes = [temp]
            self.all_nodes[0].append(temp)
            for i in range(self.level):
                temp = NonLeafNode(self.dim, self.pagesize, 0)
                nodes.append(temp)
                if i < self.level - 1:
                    self.all_nodes[i + 1].append(temp)

            line_num = 0

            for line in f:
                cols = line.strip().split(",")
                if len(cols) != self.level + self.dim:
                    continue
                # print(line)
                # print(cols, cols[0:dim], int(cols[dim]))
                obj = data_object(location=list(map(float, cols[0:self.dim])), order=order, index=int(cols[self.dim]),
                                  dim=self.dim)
                if line_num == 0:
                    nodes[0].add(obj)
                    obj.parent = nodes[0]
                    for i in range(self.level):
                        nodes[i + 1].add(nodes[i])
                        nodes[i].parent = nodes[i + 1]
                    line_num = line_num + 1
                    continue
                order = order + 1
                for i in range(self.level):
                    index = int(cols[self.dim + i])
                    # leaf node
                    if i == 0:
                        if index == before[i]:
                            nodes[i].add(obj)
                            obj.parent = nodes[i]
                            break
                        else:
                            before[i] = index
                            nodes[i].update()
                            temp = LeafNode(self.dim, self.pagesize, index)
                            nodes[i] = temp
                            self.all_nodes[i].append(temp)
                            nodes[i].parent = nodes[i + 1]
                            nodes[i].add(obj)
                            obj.parent = nodes[i]
                    else:
                        if index == before[i]:
                            nodes[i].add(nodes[i - 1])
                            break
                        else:
                            before[i] = index
                            nodes[i].update()
                            temp = NonLeafNode(self.dim, self.pagesize, index)
                            nodes[i] = temp
                            self.all_nodes[i].append(temp)
                            nodes[i].parent = nodes[i + 1]
                            nodes[i].add(nodes[i - 1])
                            if i == self.level - 1:
                                nodes[i + 1].add(nodes[i])
            self.root = nodes[self.level]
            self.root.update()

    def train_node(self, node, level, iteration, algorithm='random'):
        # if level > 3:
        if level > 2:
            for item in node.nodes:
                self.train_node(item, level - 1, iteration, algorithm)
        iteration = iteration * len(node.nodes)
        print('trained node:', node, 'level', level, 'iteration', iteration, 'algorithm', algorithm)
        # print("iteration", iteration)
        observation, original_page_size = node.reset()
        if algorithm == 'random':
            RL = random_algorithm()
            step = 0
            while True:
                if len(observation) <= 1:
                    return
                action = RL.choose_action(observation)
                observation_, reward, done = node.step_move(observation, action)
                if step > iteration or done:
                    break
                observation = observation_
                step += 1

            observation, original_page_size = node.reset()
            # print('original_page_size', original_page_size)
        elif algorithm == 'DQN':
            RL = DeepQNetwork(len(observation), len(observation))
            pre_train = 5
            for i in range(pre_train):
                for index, value in enumerate(observation):
                    action = index
                    observation_, reward, done = node.step_move(observation, action)
                    RL.store_transition(observation, action, reward*10, observation_)
                    RL.learn()
            step = 0
            while True:
                if len(observation) <= 1:
                    return
                action = RL.choose_action(observation)
                observation_, reward, done = node.step_move(observation, action)
                RL.store_transition(observation, action, reward*10, observation_)
                if (step > 200) and (step % 5 == 0):
                    RL.learn()
                if step > iteration or done:
                    break
                observation = observation_
                step += 1
        elif algorithm == 'DDPG':
            vars = [2, 3]
            LRs = [0.01, 0.001, 0.0001]
            EPSILONs = [0.1, 0.01]
            MEMORY_CAPACITYs = [5000, 10000]
            GAMMAs = [0.9]
            min_area = sys.float_info.max
            for var in vars:
                for LR in LRs:
                    for EPSILON in EPSILONs:
                        for MEMORY_CAPACITY in MEMORY_CAPACITYs:
                            for GAMMA in GAMMAs:
                                temp_area = self.DDPG(node, iteration, observation, var, LR, LR, GAMMA, MEMORY_CAPACITY,
                                                      EPSILON)
                                if temp_area < min_area:
                                    min_area = temp_area
                                    # print('var', var, 'LR', LR, 'EPSILON', EPSILON, 'MEMORY_CAPACITY', MEMORY_CAPACITY,
                                    #       'GAMMA', GAMMA, 'min_area', min_area)

        # else:

    # LR_A = 0.01 learning rate for actor
    # LR_C = 0.01  learning rate for critic'
    def DDPG(self, node, iteration, observation, var=3, LR_A=0.01, LR_C=0.01, GAMMA=0.9,
             MEMORY_CAPACITY=10000, EPSILON=0.1, VAR_DECAY=.9995):

        REPLACEMENT = [
            dict(name='soft', tau=0.01),
            dict(name='hard', rep_iter_a=600, rep_iter_c=500)
        ][0]

        RL = DeepDeterministicPolicyGradient(len(observation), len(observation), 1, LR_A, LR_C, REPLACEMENT, GAMMA,
                                             EPSILON, MEMORY_CAPACITY)
        step = 0
        pre_train = int(MEMORY_CAPACITY / len(observation))
        # print('observation before pre train ', observation)
        # print('total area before pre train:', node.get_total_area())
        min_i = 0
        original_area = node.get_total_area()
        # TODO recover from observation?
        # min_area_observation
        min_area = sys.float_info.max
        for i in range(pre_train):
            for index, value in enumerate(observation):
                action = index
                observation_, reward, done = node.step_move(observation, action)
                RL.store_transition(observation, action, reward, observation_)
                if node.get_total_area() < min_area:
                    min_area = node.get_total_area()
                    min_i = i
                    # if min_area < 2.1:
                    #     break
        # print('min_area', min_area, 'min_i', min_i)
        # print('observation after pre train ', observation)
        # print('total area after pre train:', node.get_total_area())
        while True:
            if len(observation) <= 1:
                return
            action = RL.choose_action(observation)
            # print('action', action)
            if var >= 1:
                action = np.random.randint(max(0, action - var), min(action + var, len(observation)))
            # print('action', action, 'new_action', new_action)

            # min_area after DDPG: 2.1695170604168643
            # min area step after DDPG: 9
            observation_, reward, done = node.step_move(observation, action)
            if reward != 0:
                # print(action, reward * 100)
                RL.store_transition(observation, action, reward * 100, observation_)
            if RL.M.pointer > MEMORY_CAPACITY:  # TODO M.pointer > MEMORY_CAPACITY
                var *= VAR_DECAY  # decay the action randomness
                RL.learn()
            if step > iteration or done:
                break
            observation = observation_
            step += 1
            if node.get_total_area() < min_area:
                min_area = node.get_total_area()
                min_i = step
        # print('observation finish ', observation)
        # print('min_area after DDPG:', min_area)
        # print('min area step after DDPG:', min_i)
        # print('total area after DDPG:', node.get_total_area())
        return min_area

    def train_rtree(self, iteration=800, algorithm='random'):
        print("self.root.nodes:", self.root.nodes)
        for node in self.root.nodes:
            self.train_node(node, self.level, iteration, algorithm)
        print('game over')
        return self.root

    def output_rtree(self, algorithm):
        nodes_list = [self.root]
        lines = []
        while len(nodes_list) > 0:
            temp = nodes_list.pop()
            if isinstance(temp, NonLeafNode):
                nodes_list.extend(temp.nodes)
            elif isinstance(temp, LeafNode):
                nodes_list.extend(temp.nodes)
            else:
                line = ','.join(map(str, temp.location)) + temp.get_levels(self.root)
                lines.append(line)
        lines.reverse()
        if self.output_file is None:
            paths = self.file.split('/')
            prefix = '/'.join(paths[0:-1])
            file_name = prefix + '/' + paths[-1].split('.')[0] + '_' + algorithm + '.csv'
        else:
            file_name = self.output_file
        with open(file_name, 'w') as f:
            for line in lines:
                f.write(line + '\n')


def parser(argv):
    try:
        opts, args = getopt.getopt(argv, "l:i:o:d:p:a:")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-l':
            level = int(arg)
        elif opt == '-i':
            inputfile = arg
        elif opt == '-o':
            outputfile = arg
        elif opt == '-d':
            dim = int(arg)
        elif opt == '-p':
            pagesize = int(arg)
        elif opt == '-a':
            algorithm = arg
    return inputfile, outputfile, dim, level, pagesize, algorithm


if __name__ == '__main__':
    inputfile, outputfile, dim, level, pagesize, algorithm = parser(sys.argv[1:])
    # dataset = '/Users/guanli/Documents/codes/DL_Rtree/dataset/test_tree_building.csv'
    # rtree = Rtree(dataset, dim=2, level=3)

    # inputfile = "/Users/guanli/Documents/datasets/RLRtree/trees/Z_uniform_160000_1_2_.csv"
    # outputfile = "/Users/guanli/Documents/datasets/RLRtree/newtrees/Z_uniform_160000_1_2_DDPG.csv"

    # inputfile = "D:\\datasets\\RLRtree\\trees\\Z_uniform_160000_1_2_.csv"
    # outputfile = "D:\\datasets\\RLRtree\\newtrees\\Z_uniform_160000_1_2_DDPG.csv"
    # dim = 2
    # level = 3
    # pagesize = 104
    # algorithm = "DDPG"

    print(inputfile, outputfile, dim, level, pagesize)
    # dataset = '/Users/guanli/Documents/codes/DL_Rtree/dataset/Z_normal_2000000_.csv'
    rtree = Rtree(inputfile, dim=dim, level=level, pagesize=pagesize, output_file=outputfile)
    rtree.build_rtree()
    print('build finish')
    iteration = 500
    if algorithm != 'null':
        rtree.train_rtree(iteration, algorithm)
    print('train finish')
    rtree.output_rtree(algorithm)
    print('output finish')

    # rtree.reset()
    # rtree.train_rtree(200)
    # dataset = '/Users/guanli/Documents/codes/DL_Rtree/dataset/Z_normal_2000000_.csv'
    # rtree = Rtree(dataset, dim=2, level=3)
    # rtree.build()
    # rtree.root
