import unittest
from unittest.mock import patch
from . import INTEGRATIONS
from . import dev
from .dev import esperar_temporizador, iniciar_medicion, detener_medicion
class TestTemporizador(unittest.TestCase):
    @patch.object(dev.time, "sleep")
    def test_temporizador_espera_y_devuelve_mensaje(self, mock_sleep):
        resultado = esperar_temporizador(3, "descanso")
        mock_sleep.assert_called_once_with(3)
        self.assertIn("Tiempo terminado", resultado)
        self.assertIn("descanso", resultado)
    def test_temporizador_rechaza_duracion_invalida(self):
        for valor in (0, -1, 86401):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    esperar_temporizador(valor)
    def test_temporizador_rechaza_tipo_invalido(self):
        with self.assertRaises(TypeError):
            esperar_temporizador(1.5)
class TestCronometro(unittest.TestCase):
    def setUp(self):
        dev._inicio_cronometro = None
    def tearDown(self):
        dev._inicio_cronometro = None
    @patch.object(dev.time, "monotonic", side_effect=[10.0, 12.5])
    def test_mide_tiempo_transcurrido(self, mock_clock):
        iniciar_medicion()
        resultado = detener_medicion()
        self.assertIn("00:00:02.50", resultado)
        self.assertEqual(mock_clock.call_count, 2)
    @patch.object(dev.time, "monotonic", return_value=5.0)
    def test_no_permite_iniciar_dos_veces(self, mock_clock):
        iniciar_medicion()
        with self.assertRaises(RuntimeError):
            iniciar_medicion()
    def test_no_permite_detener_si_no_se_inicio(self):
        with self.assertRaises(RuntimeError):
            detener_medicion()
class TestIntegraciones(unittest.TestCase):
    def test_registra_las_tres_acciones(self):
        nombres = [integracion.name for integracion in INTEGRATIONS]
        self.assertEqual(
            nombres,
            ["temporizador", "cronometro", "detener_cronometro"],
        )
if __name__ == "__main__":
    unittest.main()