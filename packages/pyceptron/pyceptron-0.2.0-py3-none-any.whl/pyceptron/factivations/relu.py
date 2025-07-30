from .base import ActFunctionBase
import numpy as np

class ReLU(ActFunctionBase):
  def __init__(self):
    self.function = lambda x: np.maximum(0, x)
    self._derivative_fn = lambda x: np.where(x > 0, 1, 0)

  def __repr__(self):
    return f"ReLU()"
  
  @property
  def name(self):
    return "ReLU"