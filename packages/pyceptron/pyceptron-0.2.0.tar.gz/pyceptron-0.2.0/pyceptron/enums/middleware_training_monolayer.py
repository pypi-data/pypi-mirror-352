from enum import Enum

class MiddlewareTrainingMonolayer(Enum):
  HISTORY_WEIGHTS = {"name": "history_weights", "description": "Historial de pesos", "target": "weights"}
  HISTORY_BIASES = {"name": "history_bias", "description": "Historial de bias", "target": "bias"}
  HISTORY_ERROR = {"name": "history_error", "description": "Historial de error", "target": "error"}
  HISTORY_Y_PREDICTED = {"name": "history_y_predicted", "description": "Historial de predicciones", "target": "y_pred"}
  HISTORY_Y_TRUE = {"name": "history_y_true", "description": "Historial de valores reales", "target": "y_true"}
  HISTORY_XI = {"name": "history_xi", "description": "Historial de entradas", "target": "xi"}
  HISTORY_YI = {"name": "history_yi", "description": "Historial de salidas", "target": "yi"}
  HISTORY_SSR = {"name": "history_ssr", "description": "Historial de error cuadrático", "target": "ssr"}
  HISTORY_LAST_Z = {"name": "history_last_z", "description": "Historial de la última entrada", "target": "last_z"}
  HISTORY_ALL = {"name": "history_all", "description": "Historial completo", "target": "all"}