from .base import ActFunctionBase
import numpy as np

class Sigmoid(ActFunctionBase):
  def __init__(self):
    self.function = lambda x: 1 / (1 + np.exp(-x))
    self._derivative_fn = lambda x: self(x) * (1 - self(x))  # f(x)(1 - f(x))

  def __repr__(self):
    return f"Sigmoid()"
  
  @property
  def name(self):
    return "Sigmoid"