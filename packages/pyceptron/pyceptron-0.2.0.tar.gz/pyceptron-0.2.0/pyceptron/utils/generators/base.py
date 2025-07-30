from .abs import Generator
import numpy as np

class DatasetGenerator(Generator):
  def __init__(self, function=lambda x: x):
    self.function = function
    self.x = []
    self.y = []

  def generate(self, quantity:int=10, range_start:int=-10, range_end:int=10, shuffle=False):
    # Validar que el rango sea correcto
    if range_start >= range_end:
      raise ValueError("El rango de inicio debe ser menor que el rango de fin.")
    # Validar que la cantidad sea positiva
    if quantity <= 0:
      raise ValueError("La cantidad de datos debe ser positiva.")
    # Validar que el rango no sea cero
    if range_end - range_start == 0:
      raise ValueError("El rango no puede ser cero.")
    # Validar que la longitud del rango no supere los 40 para evitar desbordamientos de memoria
    if abs(range_end) + abs(range_start) > 40:
      raise ValueError("El rango no puede ser mayor a 40 para evitar desbordamientos de memoria.")

    self.x = np.linspace(range_start, range_end, quantity)
    self.y = [self.function(xi) for xi in self.x]

    if shuffle:
      combined = list(zip(self.x, self.y))
      np.random.shuffle(combined)
      self.x, self.y = zip(*combined)

      self.x = np.array(self.x)
      self.y = np.array(self.y)

    return self.x, self.y
  
  def graph(self):
    import matplotlib.pyplot as plt
    plt.plot(self.x, self.y)
    plt.title("Dataset")
    plt.show()

  def graph_x(self):
    import matplotlib.pyplot as plt
    plt.plot(self.x)
    plt.title("Dataset Analysis X")
    plt.xlabel("X")
    plt.show()

  def graph_y(self):
    import matplotlib.pyplot as plt
    plt.plot(self.y)
    plt.title("Dataset Analysis Y")
    plt.xlabel("Y")
    plt.show()

  def expected(self, x):
    return self.function(x)
