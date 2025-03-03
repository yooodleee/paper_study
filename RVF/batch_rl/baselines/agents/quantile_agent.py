
"""
Quantile Regression Agent with logged replay buffer.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from batch_rl.baselines.replay_memory import logged_prioritized_replay_buffer
from batch_rl.multi_head import quantile_agent

import gin


@gin.configurable
class LoggedQuantileAgent(quantile_agent.QuantileAgent):
    """
    An implementation of the Quantile ageng with replay buffer logging to disk.
    """

    def __init__(
            self,
            sess,
            num_actions,
            replay_log_dir,
            **kwargs):
        
        """
        Initializes the agent and constructs the components of its graph.

        Args:
            sess(tf.Session): for executing ops.
            num_actions(int): number of actions the agent can take at any state.
            replay_log_dir(str): log Directory to save the replay buffer to disk
                periodically.
            kwargs: Arbitrary keyword arguments.
        """
        assert replay_log_dir is not None
        self._replay_log_dir = replay_log_dir
        super(LoggedQuantileAgent, self).__init__(sess, num_actions, **kwargs)

    def log_final_buffer(self):
        self._replay.memory.log_final_buffer()
    
    def _build_replay_buffer(self, use_stagining):
        """
        Creates the replay buffer used by the agent.

        Args:
            use_stagining(bool): if True, uses a stagining area to prefetch data
                for faster training.

        Returns:
            ValueError: if given an invalid replay scheme.
        """
        if self._replay_sceme not in ['uniform', 'prioritized']:
            raise ValueError(
                'Invalid replay scheme: {}'.format(self._replay_scheme)
            )
        # Both replay schemes use the same data structure, but the 'uniform' scheme
        # sets all priorities to the same value (which yields uniform sampling).
        return logged_prioritized_replay_buffer.WrappedLoggedPrioritizedReplayBuffer(
            log_dir=self._replay_log_dir,
            observation_shape=self.observation_shape,
            stack_size=self.stack_size,
            use_stagining=use_stagining,
            update_horizon=self.update_horizon,
            gamma=self.gamma,
            observation_dtype=self.observation_dtype.as_numpy_dtype,
        )