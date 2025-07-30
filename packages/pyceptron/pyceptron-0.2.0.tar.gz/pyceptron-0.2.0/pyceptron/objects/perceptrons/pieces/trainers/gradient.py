from ...models.perceptronABC import PerceptronABC
import numpy as np

class GradientTrainerPerceptronPiece(PerceptronABC):
  def train(self, x, y, alpha, epochs):
    for epoch in range(epochs):
      error_epoch = []

      for x_train, y_true in zip(x, y):
        yi_predict = self.predict(x_train)

        error = y_true-yi_predict

        gradient = self.f_activation.derivative(self.last_z)

        self.weights += error * gradient * alpha * x_train
        self.bias += error * gradient * alpha

        error_epoch.append(error)

        if self._analyzer_middleware:
          data_middleware = {
            "weights": self.weights.copy(),
            "bias": self.bias.copy(),
            "error": error,
            "y_pred": y_true,
            "y_true": y_true,
            "xi": x_train.copy(),
            "yi": yi_predict,
            "ssr": error_epoch.copy(),
            "last_z": self.last_z.copy() if isinstance(self.last_z, np.ndarray) else self.last_z,
          }
          self._compile_in_training(data_middleware)

        # - END TRAINING -
      self.error_history.append(error_epoch)
      self._verbose_train(epoch, np.mean(error_epoch), epochs)

    print ("\n" if self.verbose else "")