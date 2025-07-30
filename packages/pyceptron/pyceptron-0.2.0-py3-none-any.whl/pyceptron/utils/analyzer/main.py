from termpyx import Console
from termpyx.src.enums.color import Color

from matplotlib import pyplot as plt

from .abc_main import AnalyzerABC
from ..generators.base import DatasetGenerator

class   Analyzer(AnalyzerABC):
  def __init__(self, perceptron):
    self.perceptron = perceptron
    self.console = Console(in_debug=True)
    self.middleware_results = dict()
    self.banner()

  def banner(self):
    self.console.separator(self.perceptron.name, separator="=", length=15, color=Color.GREEN)

  def mse(self):
    error_mse = []
    for ssr in self.perceptron.error_history:
      error_mse.append(
        self.mse_calc(ssr)
      )

    plt.grid()
    plt.plot(error_mse)
    plt.title("MSE history")
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.show()
    return error_mse

  def mse_calc(self, data:list):
    return (sum([(error ** 2) for error in data]) / len(data))

  def error(self):
    history_ssr = []
    for ssr in self.perceptron.error_history:
      history_ssr.append(
        sum(ssr) / len(ssr)
      )

    #plt.grid()
    plt.plot(history_ssr)
    plt.title("Error history")
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.show()

  def error_calc(self, data:list):
    return sum(data)/len(data)

  def ssr(self):
    unit_ssr = []
    for ssr in self.perceptron.error_history:
      for d in ssr:
        unit_ssr.append(d[0])

    plt.grid()
    plt.plot(unit_ssr)
    plt.title("SSR history")
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.show()

  def history_weights(self):
    if self.middleware_results["weights"]:
      plt.grid()
      plt.plot(self.middleware_results["weights"])
      plt.title("Weights history")
      plt.xlabel('Epoch')
      plt.ylabel('Error')
      plt.show()
    else:
      self.console.info("No se han guardado los pesos durante el entrenamiento")

  def history_bias(self):
    if self.middleware_results["bias"]:
      plt.grid()
      plt.plot(self.middleware_results["bias"])
      plt.title("Bias history")
      plt.xlabel('Epoch')
      plt.ylabel('Error')
      plt.show()
    else:
      self.console.info("No se han guardado los bias durante el entrenamiento")

  def compare_graph(self, generator:DatasetGenerator):
    x_true = generator.x
    y_true = generator.y

    y_pred = [self.perceptron.predict(x) for x in generator.x]

    plt.grid()
    plt.plot(x_true, y_true, label="Linea de frontera")
    plt.plot(x_true, y_pred, label="Perceptrón")
    plt.title("Comparación de datos")
    plt.legend()
    plt.show()

  def debug(self):
    error_history = self.perceptron.error_history
    self.console.info(f"Longitud de épocas: {len(error_history)}")
    self.console.info(f"Cantidad de intentos por cada época: {len(error_history[0])}")
    self.console.info(f"Error de la última época: {self.error_calc(error_history[-1])}")
    self.console.info(f"Error cuadrático medio de la primera y última eṕoca: {self.mse_calc(error_history[0])} & {self.mse_calc(error_history[-1])}")

    # Analizando el perceptrón:
    self.console.separator("Hiperparámetros del perceptrón")
    self.console.info(f"Función de activación: {self.perceptron.f_activation}")
    self.console.info(f"Umbral: {self.perceptron.bias}")
    self.console.info(f"Pesos: {self.perceptron.weights}")

  def graph_error_list(self, error_list:list):
    plt.grid()
    plt.plot(error_list)
    plt.title("Error history")
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.show()