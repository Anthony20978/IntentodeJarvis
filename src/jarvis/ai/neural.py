import math
import random
class NeuralNetwork:
    """Red neuronal multicapa básica con propagación hacia adelante."""
    def __init__(
        self,
        layer_sizes: list[int],
        activations: list[str] | None = None,
        seed: int | None = None,
    ):
        if len(layer_sizes) < 2:
            raise ValueError("La red necesita al menos dos capas.")
        if any(
            not isinstance(size, int) or isinstance(size, bool) or size <= 0
            for size in layer_sizes
        ):
            raise ValueError("El tamaño de las capas debe ser positivo.")
        if activations is None:
            activations = ["sigmoid"] * (len(layer_sizes) - 1)
        if len(activations) != len(layer_sizes) - 1:
            raise ValueError("Cada conexión entre capas necesita una activación.")
        available = {"sigmoid", "tanh", "relu", "linear"}
        if any(name not in available for name in activations):
            raise ValueError("Función de activación no compatible.")
        self.layer_sizes = list(layer_sizes)
        self.activations = list(activations)
        generator = random.Random(seed)
        self.weights = []
        self.biases = []
        for previous_size, current_size in zip(
            layer_sizes[:-1], layer_sizes[1:]
        ):
            limit = math.sqrt(6 / (previous_size + current_size))
            layer_weights = [
                [
                    generator.uniform(-limit, limit)
                    for _ in range(previous_size)
                ]
                for _ in range(current_size)
            ]
            self.weights.append(layer_weights)
            self.biases.append([0.0] * current_size)
    @staticmethod
    def _activate(value: float, function: str) -> float:
        if function == "sigmoid":
            if value >= 0:
                return 1 / (1 + math.exp(-value))
            exp_value = math.exp(value)
            return exp_value / (1 + exp_value)
        if function == "tanh":
            return math.tanh(value)
        if function == "relu":
            return max(0.0, value)
        return value
    def predict(self, inputs: list[float]) -> list[float]:
        """Calcula la salida de la red neuronal."""
        if len(inputs) != self.layer_sizes[0]:
            raise ValueError("La cantidad de entradas no coincide con la red.")
        try:
            values = [float(value) for value in inputs]
        except (TypeError, ValueError):
            raise TypeError("Las entradas deben ser valores numéricos.") from None
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Las entradas deben ser valores finitos.")
        for weights, biases, activation in zip(
            self.weights, self.biases, self.activations
        ):
            outputs = []
            for neuron_weights, bias in zip(weights, biases):
                total = sum(
                    weight * value
                    for weight, value in zip(neuron_weights, values)
                ) + bias
                outputs.append(self._activate(total, activation))
            values = outputs
        return values