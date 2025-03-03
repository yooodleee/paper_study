"""
Components for normalize tensor.
"""
import torch
import numpy as np


class TorchRnningMeanStd:
    """
    For RND networks.
    """

    def __init__(self, shape=(), device='cpu'):
        self.device = device
        self.mean = torch.zeros(
            shape, dtype=torch.float32, device=self.device)
        self.var = torch.ones(
            shape, dtype=torch.float32, device=self.device)
        self.count = 0

        self.deltas = []
        self.min_size = 10

    @torch.no_grad()
    def update(self, x):
        x = x.to(self.device)
        batch_mean = torch.mean(x, dim=0)
        batch_var = torch.var(x, dim=0)

        # Update count and moments
        n = x.shape[0]
        self.count += n
        delta = batch_mean - self.mean
        self.mean += delta * n / self.count
        m_a = self.var * (self.count - n)
        m_b = batch_var * n
        M2 = m_a + m_b + torch.square(delta) * self.count * n / self.count
        self.var = M2 / self.count
    
    @torch.no_grad()
    def update_single(self, x):
        self.deltas.append(x)

        if len(self.deltas) >= self.min_size:
            batched_x = torch.concat(self.deltas, dim=0)
            self.update(batched_x)

            del self.deltas[:]
    
    @torch.no_grad()
    def normalize(self, x):
        return ((x.to(self.device) - self.mean) / torch.sqrt(self.var + 1e-8))


class RunningMeanStd:
    """
    For RND networks.
    """

    def __init__(self, shape=()):
        self.mean = np.zeros(shape, 'float32')
        self.var = np.ones(shape, 'float32')
        self.count = 0

        self.deltas = []
        self.min_size = 10
    
    def update(self, x):
        batch_mean = np.mean(x, axis=0)
        batch_var = np.var(x, axis=0)

        # Update count and moments
        n = x.shape[0]
        self.count += n
        delta = batch_mean - self.mean
        self.mean += delta * n / self.count
        m_a = self.var * (self.count - n)
        m_b = batch_var * n
        M2 = m_a + m_b + np.square(delta) * self.count * n / self.count
        self.var = M2 / self.count

    def update_single(self, x):
        self.deltas.append(x)

        if len(self.deltas) >= self.min_size:
            batched_x = np.stack(self.deltas, axis=0)
            self.update(batched_x)

            del self.deltas[:]
    
    def normalize(self, x):
        return (x - self.mean) / np.sqrt(self.var + 1e-8)