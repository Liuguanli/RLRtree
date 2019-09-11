from algorithms.algorithm import algorithm
import numpy as np


class random_algorithm(algorithm):

    def __init__(self):
        pass

    def choose_action(self, observation):
        # print(observation)
        return np.random.randint(0, len(observation))
