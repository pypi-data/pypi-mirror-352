from ..models.fullbase import PerceptronBase
from ..pieces.trainers.classic import ClassicTrainerPerceptronPiece

class PerceptronClassic(PerceptronBase, ClassicTrainerPerceptronPiece):
  def __init__(self, f_activation, input_units, init_random_hiperparameters = False, verbose=False):
    super().__init__(f_activation, input_units, init_random_hiperparameters, verbose)

  @property
  def name(self):
    return "Classic Perceptron"
