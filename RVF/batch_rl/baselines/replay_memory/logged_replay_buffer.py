
"""
Logged Replay Buffer.
"""

from __future__ import absolute_import
from __future__ import division 
from __future__ import print_function

import gzip
import pickle

from dopamine.replay_memory import circular_replay_buffer

import gin
import numpy as np
import tensorflow as tf


STORE_FILENAME_PREFIX = circular_replay_buffer.STORE_FILENAME_PREFIX


class OutOfGraphLoggedReplayBuffer(
    circular_replay_buffer.OutOfGraphReplayBuffer
):
    """
    Logs the replay buffer to disk everytime it's full.

    """

    def __init__(self, log_dir, *args, **kwargs):
        super(OutOfGraphLoggedReplayBuffer, self).__init__(*args, **kwargs)

        self._log_count = 0
        self._log_dir = log_dir
        tf.compat.v1.gfile.MakeDirs(self._log_dir)
    
    def add(
            self,
            observation,
            action,
            reward,
            terminal,
            *args):
        
        super(OutOfGraphLoggedReplayBuffer, self).add(
            observation, action, reward, terminal, *args
        )
        
        # Log the replay buffer to a file in self._log_dir if the replay buffer
        # is full.
        cur_size = self.add_count % self._replay_capacity
        if cur_size == self._replay_capacity - 1:
            self._log_buffer()
            self._log_count += 1
    
    def load(
            self,
            checkpoint_dir,
            suffix):
        
        super(OutOfGraphLoggedReplayBuffer, self).load(
            checkpoint_dir, suffix
        )

        self._log_count = self.add_count // self._replay_capacity
    
    def _log_buffer(self):
        """
        This method will save all the replay buffer's state in a single file.
        
        """

        checkpoint_elements = self._return_checkpointable_elements()
        for attr in checkpoint_elements:
            filename = self._generate_filename(
                self._log_dir, attr, self._log_count
            )
            with tf.compat.v1.gfile.Open(filename, 'wb') as f:
                with gzip.GzipFile(fileobj=f) as outfile:
                    # Checkpoint the np arrays in self._store with np.save instead of
                    # picking the directory is critical for file size and performance.
                    # STORE_FILENAME_PREFIX indicates that the variable is contained in
                    # self._store.
                    if attr.startswith(STORE_FILENAME_PREFIX):
                        array_name = attr[len(STORE_FILENAME_PREFIX):]
                        np.save(
                            outfile,
                            self._store[array_name],
                            allow_pickle=False,
                        )
                    
                    # Some numpy arrays might not be part of storage
                    elif isinstance(self.__dict__[attr], np.ndarray):
                        np.save(
                            outfile,
                            self.__dict__[attr],
                            allow_pickle=False,
                        )
                    
                    else:
                        pickle.dump(self.__dict__[attr], outfile)
        
        tf.compat.v1.logging.info(
            'Replay buffer logged to ckpt {number} in {dir}'.format(
                number=self._log_count,
                dir=self._log_dir,
            )
        )

    def log_final_buffer(self):
        """
        Logs the replay buffer at the end of training.
        
        """

        add_count = self.add_count
        self.add_count = np.array(self.cursor())
        self._log_buffer()
        self._log_count += 1
        self.add_count = add_count


@gin.configurable(
    denylist=[
        'observation_shape',
        'stack_size',
        'update_horizon',
        'gamma',
    ]
)

class WrappedLoggedReplayBuffer(
    circular_replay_buffer.WrappedReplayBuffer
):
    """
    Wrapped of OutOfGraphLoggedReplayBuffer with an in Graph sampling mechanism.

    """

    def __init__(
            self,
            log_dir,
            observation_shape,
            stack_size,
            use_staging=True,
            replay_capacity=1000000,
            batch_size=32,
            update_horizon=1,
            gamma=0.99,
            wrapped_memory=None,
            max_sample_attempts=1000,
            extra_storage_types=None,
            observation_dtype=np.uint8,
            action_shape=(),
            action_dtype=np.int32,
            reward_shape=(),
            reward_dtype=np.float32,
    ):
        """
        Initializes WrappedLoggedReplayBuffer.
        """

        memory = OutOfGraphLoggedReplayBuffer(
            log_dir,
            observation_shape,
            stack_size,
            replay_capacity,
            batch_size,
            update_horizon,
            gamma,
            max_sample_attempts,
            extra_storage_types=extra_storage_types,
            observation_dtype=observation_dtype,
        )

        super(WrappedLoggedReplayBuffer, self).__init__(
            observation_shape,
            stack_size,
            use_staging=use_staging,
            replay_capacity=replay_capacity,
            batch_size=batch_size,
            update_horizon=update_horizon,
            gamma=gamma,
            wrapped_memory=wrapped_memory,
            max_sample_attempts=max_sample_attempts,
            extra_storage_types=extra_storage_types,
            observation_dtype=observation_dtype,
            action_shape=action_shape,
            action_dtype=action_dtype,
            reward_shape=reward_shape,
            reward_dtype=reward_dtype,
        )