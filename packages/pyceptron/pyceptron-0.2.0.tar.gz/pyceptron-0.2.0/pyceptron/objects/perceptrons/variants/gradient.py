from ..models.fullbase import PerceptronBase
from ..pieces.trainers.gradient import GradientTrainerPerceptronPiece

class PerceptronGradient(PerceptronBase, GradientTrainerPerceptronPiece):
  def __init__(self, f_activation, input_units, init_random_hiperparameters = False, verbose=False):
    super().__init__(f_activation, input_units, init_random_hiperparameters, verbose)

  @property
  def name(self):
    return "Gradient Perceptron"