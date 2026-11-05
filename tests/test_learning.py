import unittest
from jarvis.ai.neural import NeuralNetwork
from jarvis.ai.learning import train_network
class TestLearning(unittest.TestCase):
    def test_training_reduces_loss(self):
        network = NeuralNetwork([1, 1], seed=42)
        history = train_network(
            network,
            inputs=[[0.0], [1.0]],
            targets=[[0.0], [1.0]],
            epochs=100,
            learning_rate=0.5,
        )
        self.assertLess(history[-1], history[0])
    def test_training_returns_history(self):
        network = NeuralNetwork([1, 1], seed=42)
        history = train_network(
            network,
            inputs=[[0.0]],
            targets=[[1.0]],
            epochs=5,
        )
        self.assertEqual(len(history), 5)
    def test_invalid_network(self):
        with self.assertRaises(TypeError):
            train_network(None, [[0.0]], [[1.0]])
    def test_invalid_epochs(self):
        network = NeuralNetwork([1, 1])
        with self.assertRaises(ValueError):
            train_network(network, [[0.0]], [[1.0]], epochs=0)
    def test_invalid_learning_rate(self):
        network = NeuralNetwork([1, 1])
        with self.assertRaises(ValueError):
            train_network(
                network, [[0.0]], [[1.0]], learning_rate=0
            )
    def test_mismatched_dataset_size(self):
        network = NeuralNetwork([1, 1])
        with self.assertRaises(ValueError):
            train_network(network, [[0.0], [1.0]], [[1.0]])
    def test_invalid_dimensions(self):
        network = NeuralNetwork([2, 1])
        with self.assertRaises(ValueError):
            train_network(network, [[0.0]], [[1.0]])
        with self.assertRaises(ValueError):
            train_network(network, [[0.0, 1.0]], [[1.0, 2.0]])
    def test_non_finite_values(self):
        network = NeuralNetwork([1, 1])
        with self.assertRaises(ValueError):
            train_network(network, [[float("inf")]], [[1.0]])
if __name__ == "__main__":
    unittest.main()