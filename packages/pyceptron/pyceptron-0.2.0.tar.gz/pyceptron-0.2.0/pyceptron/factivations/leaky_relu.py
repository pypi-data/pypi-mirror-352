from .base import ActFunctionBase
import numpy as np

class LeakyReLU(ActFunctionBase):
  def __init__(self, alpha=0.01):
    self.alpha = alpha
    self.function = lambda x: np.where(x > 0, x, self.alpha * x)
    self._derivative_fn = lambda x: np.where(x > 0, 1, self.alpha)

  def __repr__(self):
    return f"LeakyReLU(alpha={self.alpha})"

  @property
  def name(self):
    return "LeakyReLU"