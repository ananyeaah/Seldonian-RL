from abc import ABC

import numpy as np

from gym import spaces
import copy
from .environment import Environment

"""
A version of Gridworld with 5*5 dimensions, gamma=1 
Here rewards are -1 always, so the agent is incentivized to reach the TAS asap
Actions fail with 0.1 probability otherwise succeed
"""


class Gridworldv1(Environment):
    def __init__(self, size=5, gamma=1, discrete=True):
        self.size = int(size)
        self.x = int(0)
        self.y = int(0)
        self.count = 0
        nums = self.size ** 2
        self.nums = nums
        self.numa = 4
        self.observation_space = spaces.Box(low=np.zeros(nums), high=np.ones(nums))
        self.action_space = spaces.Discrete(self.numa)
        self._gamma = gamma
        self.numActions = 4
        self.discrete = discrete

    @property
    def name(self):
        return "Gridworldv1"

    @property
    def gamma(self) -> float:
        return self._gamma

    @property
    def isEnd(self) -> bool:
        return self.terminal()


    @property
    def horizonLength(self):
        return 500

    @property
    def state(self) -> np.ndarray:
        return np.array([self.get_state()])

    @property
    def threshold(self):
        """
        The threshold performance
        """
        return -110


    def getNumActions(self):
        return self.numActions

    def getStateDims(self):
        return self.size ** 2

    def reset(self):
        self.x = 0
        self.y = 0
        self.count = 0
        return self.get_state()

    def step(self, action):
        self.count += 1
        a = int(action)
        s = np.random.uniform(0, 1)

        # agent breaks down and fails to act
        if s < 0.1:
            r=-1
            return self.get_state(), r, self.terminal()

        # agent takes action successfully
        if a == 0:
            self.y -= 1
        elif a == 1:
            self.y += 1
        elif a == 2:
            self.x -= 1
        elif a == 3:
            self.x += 1
        else:
            raise Exception("Action out of range! Must be in [0,3]: " + a)


        self.x = int(np.clip(self.x, 0, self.size - 1))
        self.y = int(np.clip(self.y, 0, self.size - 1))

        reward = -1.0

        return self.get_state(), reward, self.terminal()


    def nextState(self, state, action):
        s,_,_ = self.step(action)
        return s

    def get_state(self):
        x = np.zeros(self.nums, dtype=np.float32)
        x[self.x * self.size + self.y] = 1

        return x


    def terminal(self):
        return (self.x == self.size - 1 and self.y == self.size - 1) or (self.count > 500)


    def R(self, state, action, nextState):
        return -1

    def getDiscreteState(self, state):
        return np.argmax(state)

    def getNumDiscreteStates(self):
        return self.getStateDims()
