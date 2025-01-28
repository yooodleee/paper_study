import numpy as np
from rllab.envs.base import Env
from rllab.spaces import Box
from rllab.envs.base import Step
from rllab.core.serializable import Serializable
import tensorflow as tf


ctrl_cost_coeff = 0.01
goal = np.array([8., 5.])


class Point2DEnv(Env, Serializable):

    def __init__(self):
        Serializable.quick_init(self, locals())
        self.state = None
        """
        x_next = Ax + Bu + c + D*noise
        """
        self.transition = {
            'A': np.array([[1., 0.03], [0., 1.]]),
            'B': np.array([[1., 0.], [0., 1.]]),
            'c': np.array([0., 0.]),
        }
        self.goal = goal
        self.init_mean = np.zeros(2)
        self.init_std = 0.1
        self.ctrl_cost_coeff = ctrl_cost_coeff
    
    def reset(self, init_state=None):
        if init_state is None:
            self.state = self.init_mean + np.random.randn(2) * self.init_std
        else:
            self.state = init_state
        return self.state
    
    def step(self, action):
        assert self.state is not None, "call env.reset before step."
        # Clipping action
        action = np.clip(action, *self.action_space.bounds)
        action = np.reshape(action, -1)
        next_state = self.transition['A']@self.state + \
                     self.transition['B']@action + \
                     self.transition['c']
        next_state = np.clip(next_state, *self.observation_space.bounds)
        self.state = next_state
        return Step(
            observation=self.get_obs(),
            reward=self.get_reward(action),
            done=False,
        )
    
    