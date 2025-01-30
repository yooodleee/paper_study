from abc import ABC, abstractmethod
from baselines.common.title_images import title_images


class AlreadySteppingError(Exception):
    """
    Raised when an asynchronous step is running while
        step_async() is called again.

    """

    def __init__(self):
        msg = 'already running an async step'
        Exception.__init__(self, msg)
    

class NotSteppingError(Exception):
    """
    Raised when an asynchronous step is not running but
        step_wait() is called.

    """

    def __init__(self):
        msg = 'not running an async step'
        Exception.__init__(self, msg)


class VecEnv(ABC):
    """
    An abstract asynchronous, vectorized environment.
    Used to batch data from multiple copies of an environment, so that
        each observation becomes an batch of observations, and expected
        action is a batch of actions to be applied per-environment.

    """
    closed = False
    viewer = None

    metadata = {
        'render.modes': ['human', 'rgb_array']
    }

    def __init__(
            self,
            num_envs,
            observation_space,
            action_space):
        
        self.num_envs = num_envs
        self.observation_space = observation_space
        self.action_space = action_space
    
    @abstractmethod
    def reset(self):
        """
        Reset all the environments and return an array of
            observations, or a dict of observation arrays.

        If step_async is still doing work, that work will
            be cancelled and step_wait() should not be called
            untill step_async() is invoked again.

        """
        pass

    @abstractmethod
    def step_async(self, actions):
        """
        Tell all the environments to start taking a step with the
            given actions. Call step_wait() to get the results of
            the step.

        You should not call this if a step_async run is already 
            pending.

        """
        pass

    @abstractmethod
    def step_wait(self):
        """
        Wait for the step taken with step_async().

        Returns
        -------------
        obs: an array of observations, or a dict of arrays of 
            observations.
        rews: an array or rewards.
        dones: an array of "episode done" booleans.
        infos: a sequence of info objects.

        """
        pass

    def close_extras(self):
        """
        Clean up the extra resources, beyound what's in this base class.
        Only runs when not self.closed.
        """
        pass

    def close(self):
        if self.closed:
            return
        
        if self.viewer is not None:
            self.viewer.close()
        
        self.close_extras()
        self.closed = True
    
    def step(self, actions):
        """
        Step the environments synchronously.

        This is available for backwards compatibility.

        """
        self.step_async(actions)
        return self.step_wait()
    
    def render(self, mode='human'):
        imgs = self.get_images()
        bigimg = title_images(imgs)
        if mode == 'human':
            self.get_viewer().imshow(bigimg)
            return self.get_viewer().isopen
        
        elif mode == 'rgb_array':
            return bigimg
        
        else:
            raise NotImplementedError
    
    def get_images(self):
        """
        Return RGB images from each environment.
        """
        raise NotImplementedError
    
    @property
    def unwrapped(self):
        if isinstance(self, VecEnvWrapper):
            return self.venv.unwrapped        
        else:
            return self
    
    def get_viewer(self):
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            
            self.viewer = rendering.SimpleImageViewer()
        return self.viewer


