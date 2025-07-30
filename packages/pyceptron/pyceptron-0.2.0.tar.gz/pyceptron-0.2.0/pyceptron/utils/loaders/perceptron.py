from os.path import exists
import json

class ImporterPerceptron:
  def __init__(self, data:dict):
    self.data = data
    self._process()

  def _process(self):
    self.name = self.data.get("name")
    self.f_activation = self.data.get("f_activation")
    self.weights = self.data.get("weights")
    self.bias = self.data.get("bias")    

  def list_variants(self):
    from pyceptron.objects.perceptrons.variants.classic import PerceptronClassic
    from pyceptron.objects.perceptrons.variants.gradient import PerceptronGradient    
    collection_variants = {
      "Gradient Perceptron": PerceptronGradient,
      "Classic Perceptron": PerceptronClassic
    }
    return collection_variants

  def list_activations(self):
    from pyceptron import ReLU, LeakyReLU, Linear, ELU, Sigmoid, Tanh

    collection_activations = {
      "ReLU": ReLU,
      "LeakyReLU": LeakyReLU,
      "Linear": Linear,
      "ELU": ELU,
      "Sigmoid": Sigmoid,
      "Tanh": Tanh
    }
    return collection_activations
  
  def to_perceptron(self):
    variants = self.list_variants()
    activations = self.list_activations()

    activation = activations.get(self.f_activation)
    if not activation:
      raise TypeError("Activation function not supported yet.")
    
    perceptron = variants.get(self.name)
    if not perceptron:
      raise TypeError("Type Perceptron is not supported yet.")
    
    cf_perceptron = perceptron(f_activation=activation(), input_units=len(self.weights), verbose=False)
    cf_perceptron.weights = self.weights
    cf_perceptron.bias = self.bias

    return cf_perceptron

  def __repr__(self):
    return f"{self.name}(weights={self.weights}, bias={self.bias}, f_activation={self.f_activation})"
  
def load_perceptron(route:str):
  if not exists(route):
    raise FileNotFoundError("Perceptron not found in '{}'".format(route))
  
  data = json.load(open(route, "r"))
  importer = ImporterPerceptron(data)

  return importer.to_perceptron()