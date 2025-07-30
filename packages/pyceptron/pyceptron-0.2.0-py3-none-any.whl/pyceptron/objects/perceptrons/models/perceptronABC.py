from ....factivations.abs import Function_activationABC
from abc import ABC, abstractmethod
from ....utils.analyzer.abc_main import AnalyzerABC
from ....enums.middleware_training_monolayer import MiddlewareTrainingMonolayer
import numpy as np

class PerceptronABC(ABC):
    """
    Clase abstracta base para la implementación de un perceptrón.

    Define la estructura que debe seguir cualquier implementación de un perceptrón,
    incluyendo métodos esenciales para inicialización de parámetros, entrenamiento,
    predicción y middleware de análisis durante el entrenamiento.
    """

    def __init__(
        self,
        f_activation: Function_activationABC,
        input_units: int,
        init_random_hiperparameters: bool = False,
        verbose: bool = False
    ):
        """
        Inicializa la clase base del perceptrón.

        :param f_activation: Función de activación utilizada por el perceptrón.
        :param input_units: Número de entradas del perceptrón.
        :param init_random_hiperparameters: Si True, inicializa pesos y bias aleatoriamente.
        :param verbose: Si True, muestra información durante el entrenamiento.
        """
        self.verbose = verbose
        self.f_activation:Function_activationABC = f_activation
        self.units = input_units
        self.weights:np.ndarray = None
        self.bias = None

        self.last_z = None

        self.error_history:list[list[np.ndarray]] = None
        self._analyzer_middleware:AnalyzerABC = None
        self._options_middleware = None

    @abstractmethod
    def _bias(self, init_random: bool):
        """
        Inicializa el sesgo (bias) del perceptrón.

        :param init_random: Si es True, se inicializa aleatoriamente; de lo contrario, se inicializa en cero.
        :return: Valor de sesgo inicializado.
        """
        pass

    @abstractmethod
    def _weights(self, input_units, init_random: bool):
        """
        Inicializa los pesos del perceptrón.

        :param input_units: Número de unidades de entrada.
        :param init_random: Si es True, se inicializan aleatoriamente; de lo contrario, se inicializan en cero.
        :return: Vector de pesos.
        """
        pass

    @abstractmethod
    def _verbose_train(self, epoch, error=1, epochs=1):
        """
        Muestra información del entrenamiento si el modo verbose está activado.

        :param epoch: Época actual.
        :param error: Error actual.
        :param epochs: Número total de épocas.
        """
        pass

    @abstractmethod
    def linear_combination(self, x):
        """
        Calcula la combinación lineal entre las entradas y los pesos, sumando el sesgo.

        :param x: Vector de entrada.
        :return: Resultado de la combinación lineal.
        """
        pass

    @abstractmethod
    def in_training(self, analyzer: AnalyzerABC = None, options: list[MiddlewareTrainingMonolayer] = []):
        """
        Habilita el análisis en tiempo real durante el entrenamiento utilizando un analizador y opciones de middleware.

        :param analyzer: Instancia de AnalyzerABC que gestiona la recopilación de datos.
        :param options: Lista de MiddlewareTrainingMonolayer que define qué datos serán recopilados.
        :raises ValueError: Si no se especifican opciones cuando se pasa un analizador.
        """
        pass

    @abstractmethod
    def _compile_in_training(self, data_middleware: dict):
        """
        Compila los datos generados durante el entrenamiento y los pasa al middleware del analizador.

        :param data_middleware: Diccionario con los datos recopilados del estado actual del entrenamiento.
        """
        pass

    @abstractmethod
    def train(self, x:list, y:list, alpha:float, epochs:int):
        """
        Entrena el perceptrón usando el algoritmo de aprendizaje supervisado.

        :param x: Datos de entrada.
        :param y: Etiquetas verdaderas correspondientes.
        :param alpha: Tasa de aprendizaje.
        :param epochs: Número de épocas de entrenamiento.
        """
        pass

    @abstractmethod
    def predict(self, x):
        """
        Realiza una predicción usando el perceptrón entrenado.

        :param x: Vector de entrada.
        :return: Salida predicha por el perceptrón.
        """
        pass

    @property
    def name(self):
        return "Abstract Perceptron"