from .abs import Function_activationABC

class ActFunctionBase(Function_activationABC):
  def __init__(self):
    self.function: callable = None 
    self._derivative_fn: callable = None

  def __call__(self, x):
    return self.function(x)

  def derivative(self, x):
    return self._derivative_fn(x)

  def __repr__(self):
    return f"ActFunctionBase({self.function.__name__}, {self._derivative_fn.__name__})"

  @property
  def name(self):
    return "ActFunctionBase"