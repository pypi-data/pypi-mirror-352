from .objects.perceptrons.variants.classic import PerceptronClassic
from .objects.perceptrons.variants.gradient import PerceptronGradient
from .factivations import ReLU, LeakyReLU, ELU, ActFunctionBase, Linear, Sigmoid, Tanh

from .objects.layers.layer import Layer
from .objects.layers.sequential import Sequential
from .enums.middleware_training_monolayer import MiddlewareTrainingMonolayer