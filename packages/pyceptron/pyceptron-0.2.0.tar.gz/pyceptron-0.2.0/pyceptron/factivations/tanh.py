from .base import ActFunctionBase
import numpy as np

class Tanh(ActFunctionBase):
  def __init__(self):
    self.function = lambda x: np.tanh(x)
    self._derivative_fn = lambda x: 1 - np.tanh(x) ** 2

  def __repr__(self):
    return f"Tanh()"
  
  @property
  def name(self):
    return "Tanh"