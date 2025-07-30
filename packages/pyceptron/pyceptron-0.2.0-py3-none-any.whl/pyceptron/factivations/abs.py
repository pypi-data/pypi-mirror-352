from abc import ABC, abstractmethod

class Function_activationABC(ABC):
  def __init__(self):
    pass

  @abstractmethod
  def derivative(self, x):
    pass

  @abstractmethod
  def __call__(self, x):
    pass

  @property
  def name(self):
    return "BaseActivation"