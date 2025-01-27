# coding=utf-8
# Copyright 2021 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
The entry point for running experiments for collecting replay datasets.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import os

from absl import app
from absl import flags

from batch_rl.baselines.agents import dqn_agent
from batch_rl.baselines.agents import quantile_agent
from batch_rl.baselines.agents import random_agent
from batch_rl.baselines.run_experiment import LoggedRunner

from dopamine.discrete_domains import run_experiment
from dopamine.discrete_domains import train as base_train
import tensorflow as tf


flags.DEFINE_string('agent_name', 'dqn', 'Name of the agent.')
FLAGS = flags.FLAGS


def create_agent(
        sess,
        environment,
        replay_log_dir,
        summary_writer=None):
    
    """
    Creates a DQN agent.

    Args:
        sess: A 'tf.Session' object for running associated ops.
        environment: An Atari 2600 environment.
        replay_log_dir: Directory to which log the replay buffers periodically.
        summary_writer: A Tensorflow summary writer to pass to the agent
            for in=agent training statistics in Tensorboard.

    Returns:
        A DQN agent with metrics.
    """
    if FLAGS.agent_name == 'dqn':
        agent = dqn_agent.LoggedDQNAgent
    elif FLAGS.agent_name == 'quantile':
        agent = quantile_agent.LoggedQuantileAgent
    elif FLAGS.agent_name == 'random':
        agent = random_agent.RandomAgent
    else:
        raise ValueError(
            '{} is not a valid agent name'.format(FLAGS.agent_name)
        )
    
    return agent(
        sess,
        num_actions=environment.action_space.n,
        replay_log_dir=replay_log_dir,
        summary_writer=summary_writer,
    )


