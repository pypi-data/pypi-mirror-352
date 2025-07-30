from ..models.perceptronABC import PerceptronABC
from ....utils.analyzer.abc_main import AnalyzerABC
from ....enums.middleware_training_monolayer import MiddlewareTrainingMonolayer
from ....factivations.abs import Function_activationABC

import numpy as np

class CorePerceptronBasePiece(PerceptronABC):
  def __init__(self, f_activation:Function_activationABC, input_units:int, init_random_hiperparameters:bool=False, verbose:bool=False):
    self.verbose = verbose
    self.f_activation = f_activation
    self.units = input_units
    self.weights:np.ndarray = self._weights(input_units, init_random_hiperparameters)
    self.bias = self._bias(init_random_hiperparameters)

    self.last_z = 0

    self.error_history:list[list[np.ndarray]] = []
    self._analyzer_middleware = None
    self._options_middleware = []

  def _bias(self, init_random:bool):
    return 0 if not init_random else np.random.rand()
  
  def _weights(self, input_units, init_random:bool):
    a = np.random.rand(input_units) if init_random else np.zeros(input_units)
    return a

  def _verbose_train(self, epoch, error=1, epochs=1):
    print(f"\r[ Epoch: {epoch+1}/{epochs} | Error: {error} ]", end="")

  def linear_combination(self, x):
    return np.dot(x, self.weights) + self.bias

  def predict(self, x):
    self.last_z = x
    dot = self.linear_combination(x)
    return self.f_activation(dot)
  
  def in_training(self, analyzer:AnalyzerABC=None, options:list[MiddlewareTrainingMonolayer]=[]):
    if analyzer:
      analyzer.console.in_debug = self.verbose
      if not options:
        raise ValueError("¡Define las operaciones que serán ejecutadas durante el entrenamiento!")
      
    self._analyzer_middleware = analyzer
    self._options_middleware = options

  def _compile_in_training(self, data_middleware:dict):
    for option in self._options_middleware:
      if option.value["target"] not in self._analyzer_middleware.middleware_results:
        self._analyzer_middleware.middleware_results[option.value["target"]] = []
      
      q_data = data_middleware[option.value['target']]
      self._analyzer_middleware.console.debug(f"Compiling {option.value['target']} -> {q_data}")
      self._analyzer_middleware.middleware_results[option.value["target"]].append(q_data)

  @property
  def name(self):
    return "Core Perceptron Base"
  
  def __repr__(self):
    return f"CorePerceptron(f_activation={self.f_activation}, input_units={self.units}, weights={self.weights}, bias={self.bias})"
