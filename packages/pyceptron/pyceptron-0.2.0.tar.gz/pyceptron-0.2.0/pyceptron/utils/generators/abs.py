from abc import ABC, abstractmethod

class Generator(ABC):
  def __init__(self, function: callable):
    pass

  @abstractmethod
  def generate(self, quantity: int):
    pass    