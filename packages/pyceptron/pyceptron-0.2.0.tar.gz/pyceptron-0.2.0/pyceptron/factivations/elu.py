from .base import ActFunctionBase
import numpy as np

class ELU(ActFunctionBase):
  def __init__(self, alpha=1.0):
    self.alpha = alpha
    self.function = lambda x: np.where(x > 0, x, self.alpha * (np.exp(x) - 1))
    self._derivative_fn = lambda x: np.where(x > 0, 1, self.alpha * np.exp(x))

  def __repr__(self):
    return f"ELU(alpha={self.alpha})"

  @property
  def name(self):
    return "ELU"