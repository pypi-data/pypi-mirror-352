from abc import ABC, abstractmethod
from ...utils.generators import DatasetGenerator
from termpyx import Console

class AnalyzerABC(ABC):
    """
    Clase abstracta base para analizadores de perceptrones.

    Esta clase define una interfaz estándar para implementar diferentes análisis
    sobre el entrenamiento de un perceptrón, incluyendo cálculo de errores, visualización
    de métricas, y depuración de información.

    Attributes:
        perceptron (PerceptronABC): Instancia del perceptrón a analizar.
    """

    def __init__(self, perceptron):
        self.perceptron = perceptron
        self.console:Console = None
        self.middleware_results:dict = None
        """
        Inicializa el analizador con una instancia de perceptrón.

        Args:
            perceptron (PerceptronABC): El perceptrón del que se analizarán los resultados.
        """
        pass

    @abstractmethod
    def mse(self):
        """
        Calcula y grafica el error cuadrático medio (MSE) por época.

        Returns:
            list: Lista de valores MSE por cada época.
        """
        pass

    @abstractmethod
    def mse_calc(self, data: list):
        """
        Calcula el error cuadrático medio (MSE) a partir de una lista de errores.

        Args:
            data (list): Lista de errores individuales.

        Returns:
            float: Valor del MSE.
        """
        pass

    @abstractmethod
    def error(self):
        """
        Grafica el error promedio por época.
        """
        pass

    @abstractmethod
    def error_calc(self, data: list):
        """
        Calcula el error promedio a partir de una lista de errores.

        Args:
            data (list): Lista de errores individuales.

        Returns:
            float: Valor del error promedio.
        """
        pass

    @abstractmethod
    def ssr(self):
        """
        Grafica la suma de los errores cuadráticos individuales (SSR) durante el entrenamiento.
        """
        pass

    @abstractmethod
    def history_weights(self):
        """
        Grafica la evolución de los pesos del perceptrón durante el entrenamiento.
        """
        pass

    @abstractmethod
    def history_bias(self):
        """
        Grafica la evolución del sesgo (bias) del perceptrón durante el entrenamiento.
        """
        pass

    @abstractmethod
    def compare_graph(self, generator: DatasetGenerator):
        """
        Compara gráficamente la salida esperada y la salida del perceptrón.

        Args:
            generator (DatasetGenerator): Generador que contiene los datos reales (x, y).
        """
        pass

    @abstractmethod
    def debug(self):
        """
        Muestra en consola detalles del entrenamiento y del estado actual del perceptrón.
        """
        pass

    @abstractmethod
    def graph_error_list(self, error_list: list):
        """
        Grafica una lista arbitraria de errores.

        Args:
            error_list (list): Lista de errores por época a graficar.
        """
        pass
