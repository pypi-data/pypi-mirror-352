from ...factivations.relu import ReLU, ActFunctionBase
from ..perceptrons.variants.gradient import PerceptronGradient

class Layer:
  def __init__(self, units:int, activation:ActFunctionBase=ReLU(), input_units:int=0):
    self.units = units
    self.activation = activation
    self.sinaptic_conections:int = input_units

    self.perceptrones:list[PerceptronGradient] = self._generate_perceptrons()

  def _generate_perceptrons(self):
    return [
      PerceptronGradient(f_activation=self.activation, input_units=1, init_random_hiperparameters=True) for _ in range(self.units)
    ]

  def __repr__(self):
    return f"Layer(units={self.units}, f_activation={self.activation}, sinaptic_conections={self.sinaptic_conections})"