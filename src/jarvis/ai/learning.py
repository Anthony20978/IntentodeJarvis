import math
from .neural import NeuralNetwork
def _derivative(value: float, activation: str) -> float:
    """Calcula la derivada de una función de activación."""
    if activation == "sigmoid":
        return value * (1.0 - value)
    if activation == "tanh":
        return 1.0 - value ** 2
    if activation == "relu":
        return 1.0 if value > 0 else 0.0
    return 1.0
def train_network(
    network: NeuralNetwork,
    inputs: list[list[float]],
    targets: list[list[float]],
    epochs: int = 1000,
    learning_rate: float = 0.1,
) -> list[float]:
    """Entrena una red neuronal mediante retropropagación."""
    if not isinstance(network, NeuralNetwork):
        raise TypeError("Se esperaba una red neuronal NeuralNetwork.")
    if not isinstance(epochs, int) or isinstance(epochs, bool) or epochs <= 0:
        raise ValueError("Las épocas deben ser un entero positivo.")
    if (
        isinstance(learning_rate, bool)
        or not isinstance(learning_rate, (int, float))
        or not math.isfinite(learning_rate)
        or learning_rate <= 0
    ):
        raise ValueError("La tasa de aprendizaje debe ser positiva y finita.")
    if not isinstance(inputs, list) or not isinstance(targets, list):
        raise TypeError("Los datos deben proporcionarse mediante listas.")
    if not inputs or len(inputs) != len(targets):
        raise ValueError("Se necesita la misma cantidad de entradas y objetivos.")
    input_data = []
    target_data = []
    for sample, target in zip(inputs, targets):
        if not isinstance(sample, (list, tuple)):
            raise TypeError("Cada entrada debe ser una lista de valores.")
        if not isinstance(target, (list, tuple)):
            raise TypeError("Cada objetivo debe ser una lista de valores.")
        if len(sample) != network.layer_sizes[0]:
            raise ValueError("Una entrada tiene dimensiones incorrectas.")
        if len(target) != network.layer_sizes[-1]:
            raise ValueError("Un objetivo tiene dimensiones incorrectas.")
        try:
            sample = [float(value) for value in sample]
            target = [float(value) for value in target]
        except (TypeError, ValueError):
            raise TypeError("Los datos deben ser numéricos.") from None
        if not all(math.isfinite(value) for value in sample + target):
            raise ValueError("Los datos deben contener valores finitos.")
        input_data.append(sample)
        target_data.append(target)
    history = []
    sample_count = len(input_data)
    for _ in range(epochs):
        weight_gradients = [
            [[0.0] * len(weights[0]) for _ in weights]
            for weights in network.weights
        ]
        bias_gradients = [
            [0.0] * len(biases)
            for biases in network.biases
        ]
        total_loss = 0.0
        for sample, target in zip(input_data, target_data):
            activations = [sample]
            pre_activations = []
            values = sample
            # Propagación hacia adelante.
            for weights, biases, activation in zip(
                network.weights,
                network.biases,
                network.activations,
            ):
                outputs = []
                layer_inputs = []
                for neuron_weights, bias in zip(weights, biases):
                    total = sum(
                        weight * value
                        for weight, value in zip(neuron_weights, values)
                    ) + bias
                    layer_inputs.append(total)
                    outputs.append(network._activate(total, activation))
                pre_activations.append(layer_inputs)
                activations.append(outputs)
                values = outputs
            # Calcular el error.
            for predicted, expected in zip(values, target):
                total_loss += (predicted - expected) ** 2
            # Retropropagación del error.
            deltas = [None] * len(network.weights)
            last_layer = len(network.weights) - 1
            output_size = network.layer_sizes[-1]
            deltas[last_layer] = [
                (2.0 / output_size)
                * (predicted - expected)
                * _derivative(predicted, network.activations[last_layer])
                for predicted, expected in zip(values, target)
            ]
            for layer in range(last_layer - 1, -1, -1):
                deltas[layer] = []
                for neuron_index, output in enumerate(activations[layer + 1]):
                    error = sum(
                        network.weights[layer + 1][next_neuron][neuron_index]
                        * deltas[layer + 1][next_neuron]
                        for next_neuron in range(len(deltas[layer + 1]))
                    )
                    derivative = _derivative(
                        output,
                        network.activations[layer],
                    )
                    deltas[layer].append(error * derivative)
            # Acumular gradientes.
            for layer, layer_deltas in enumerate(deltas):
                for neuron, delta in enumerate(layer_deltas):
                    bias_gradients[layer][neuron] += delta
                    for index, previous_output in enumerate(activations[layer]):
                        weight_gradients[layer][neuron][index] += (
                            delta * previous_output
                        )
        # Actualizar pesos y sesgos.
        for layer in range(len(network.weights)):
            for neuron in range(len(network.weights[layer])):
                network.biases[layer][neuron] -= (
                    learning_rate
                    * bias_gradients[layer][neuron]
                    / sample_count
                )
                for index in range(len(network.weights[layer][neuron])):
                    network.weights[layer][neuron][index] -= (
                        learning_rate
                        * weight_gradients[layer][neuron][index]
                        / sample_count
                    )
        history.append(total_loss / (sample_count * network.layer_sizes[-1]))
    return history