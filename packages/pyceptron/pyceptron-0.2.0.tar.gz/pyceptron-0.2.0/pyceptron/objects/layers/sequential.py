from .layer import Layer
import numpy as np

class Sequential:
    def __init__(self):
        self.layers: list[Layer] = []
        self._last_input_dims: int = -1  # Tracks output dims of the last added layer

    def train(self, epochs: int = 10):
        pass

    def predict(self, x: np.array):
        return self._pre_forward(x)

    def add_layers(self, layers: Layer | list[Layer]):
        if isinstance(layers, list):
            for layer in layers:
                self._add_single_layer(layer)
        else:
            self._add_single_layer(layers)

    def _add_single_layer(self, layer: Layer):
        # Validate and auto-infer input units (sinaptic_conections) if not set
        if layer.sinaptic_conections == 0:
            if self._last_input_dims == -1:
                raise ValueError("First layer must define `sinaptic_conections` (input units).")
            else:
                # Auto-infer input units from previous layer's output
                layer.sinaptic_conections = self._last_input_dims
        # Update last_input_dims to current layer's output units
        self._last_input_dims = layer.units
        self.layers.append(layer)

    def _pre_forward(self, x: np.array):
        last_input = x
        for layer in self.layers:
            # Each layer processes the output of the previous layer
            layer_output = np.array([
                perceptron.predict(last_input)
                for perceptron in layer.perceptrones
            ])
            last_input = layer_output
        return last_input

    def __repr__(self):
        return f"Sequential(layers={len(self.layers)})"