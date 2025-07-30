from ...models.perceptronABC import PerceptronABC
import numpy as np

class ClassicTrainerPerceptronPiece(PerceptronABC):
  def train(self, x, y, alpha, epochs):
    for _ in range(epochs):
      ssr = list()
      for xi, yi in zip(x, y):
        # - TRAINING -
        y_pred = self.predict(xi)

        error = yi - y_pred
        self.weights += alpha * error * xi
        self.bias += alpha * error

        ssr.append(error)

        if self._analyzer_middleware:
          data_middleware = {
            "weights": self.weights.copy(),
            "bias": self.bias.copy(),
            "error": error,
            "y_pred": y_pred,
            "y_true": yi,
            "xi": xi.copy(),
            "yi": yi,
            "ssr": ssr.copy(),
            "last_z": self.last_z.copy() if isinstance(self.last_z, np.ndarray) else self.last_z,
          }
          self._compile_in_training(data_middleware)

        # - END TRAINING -
      self.error_history.append(ssr)
      self._verbose_train(_, np.mean(ssr), epochs)

    print ("\n" if self.verbose else "")