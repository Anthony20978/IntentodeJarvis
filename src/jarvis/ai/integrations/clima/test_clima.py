import unittest
from unittest.mock import patch
from . import INTEGRATIONS
from . import dev as dev_module, integration as integration_module
from .dev import obtener_clima
from .integration import consultar_clima
class TestClima(unittest.TestCase):
    def test_city_required(self):
        with self.assertRaises(ValueError):
            obtener_clima(" ")
    @patch.object(dev_module, "_get_json")
    def test_weather_format(self, mock_get):
        mock_get.side_effect = [
            {"results": [{
                "name": "San José", "admin1": "San José",
                "country": "Costa Rica", "latitude": 9.9, "longitude": -84.1,
            }]},
            {
                "current": {
                    "temperature_2m": 25, "relative_humidity_2m": 70,
                    "apparent_temperature": 27, "wind_speed_10m": 8,
                    "precipitation": 0, "weather_code": 2,
                },
                "daily": {"precipitation_probability_max": [30]},
            },
        ]
        resultado = obtener_clima("San José")
        self.assertIn("San José", resultado)
        self.assertIn("25 °C", resultado)
        self.assertIn("Humedad: 70%", resultado)
        self.assertIn("30%", resultado)
    @patch.object(dev_module, "_get_json")
    def test_city_not_found(self, mock_get):
        mock_get.return_value = {"results": []}
        self.assertIn("No encontré la ciudad", obtener_clima("CiudadInventada"))
    @patch.object(integration_module, "obtener_clima")
    def test_handler(self, mock_weather):
        mock_weather.return_value = "Clima de prueba"
        self.assertEqual(consultar_clima({"ciudad": "Cartago"}), "Clima de prueba")
        mock_weather.assert_called_once_with("Cartago")
    def test_definition(self):
        self.assertEqual(len(INTEGRATIONS), 1)
        self.assertEqual(INTEGRATIONS[0].name, "clima")
        self.assertIs(INTEGRATIONS[0].handler, consultar_clima)
        self.assertEqual(INTEGRATIONS[0].parameters[0].flag, "-c")
if __name__ == "__main__":
    unittest.main()