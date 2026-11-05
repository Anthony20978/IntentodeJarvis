import math
import unittest
from jarvis.ai.neural import NeuralNetwork
class TestNeuralNetwork(unittest.TestCase):
    def test_network_creation(self):
        network = NeuralNetwork([2, 3, 1], seed=42)
        self.assertIsInstance(network, NeuralNetwork)
    def test_prediction_output_size(self):
        network = NeuralNetwork([2, 3, 1], seed=42)
        result = network.predict([0.5, 0.8])
        self.assertEqual(len(result), 1)
    def test_default_sigmoid_range(self):
        network = NeuralNetwork([2, 3, 2], seed=42)
        result = network.predict([0.5, 0.8])
        for value in result:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
    def test_reproducible_with_seed(self):
        network_a = NeuralNetwork([2, 3, 1], seed=42)
        network_b = NeuralNetwork([2, 3, 1], seed=42)
        result_a = network_a.predict([0.5, 0.8])
        result_b = network_b.predict([0.5, 0.8])
        self.assertEqual(result_a, result_b)
    def test_invalid_layer_sizes(self):
        with self.assertRaises(ValueError):
            NeuralNetwork([3])
        with self.assertRaises(ValueError):
            NeuralNetwork([2, 0, 1])
    def test_invalid_activation(self):
        with self.assertRaises(ValueError):
            NeuralNetwork([2, 1], activations=["invalid"])
    def test_invalid_input_size(self):
        network = NeuralNetwork([2, 3, 1])
        with self.assertRaises(ValueError):
            network.predict([0.5])
    def test_invalid_input_values(self):
        network = NeuralNetwork([2, 1])
        with self.assertRaises((TypeError, ValueError)):
            network.predict([0.5, "texto"])
        with self.assertRaises((TypeError, ValueError)):
            network.predict([0.5, math.inf])
if __name__ == "__main__":
    unittest.main()