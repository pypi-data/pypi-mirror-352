from ..pieces.base import CorePerceptronBasePiece
from ..pieces.exporter import ExportPerceptronPiece

class PerceptronBase(CorePerceptronBasePiece, ExportPerceptronPiece):
  @property
  def name(self):
    return "Perceptron Base"
  
  def __repr__(self):
    return f"Perceptron(f_activation={self.f_activation}, input_units={self.units}, weights={self.weights}, bias={self.bias})"
