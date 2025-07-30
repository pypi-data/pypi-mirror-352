from .base import DatasetGenerator

# -- Linear --

class Celsius2FahrenheitGenerator(DatasetGenerator):
  def __init__(self, function=lambda x : x * 9/5 + 32):
    self.function = function

class Equation1Generator(DatasetGenerator):
  def __init__(self, function=lambda x : x * 251 - 220):
    self.function = function

# -- Parabola --

class Parabola1Generator(DatasetGenerator):
  def __init__(self, function=lambda x : x**2 + x*3 + 5):
    self.function = function
