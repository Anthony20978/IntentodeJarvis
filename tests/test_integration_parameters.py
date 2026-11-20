import unittest
from datetime import datetime
from unittest.mock import patch
from jarvis.ai.core import AICore
from jarvis.ai.structures import InputData, IntegrationDefinition, IntegrationParameter, AnalysisResult
from jarvis.ai.reasoning import create_action_plan
from jarvis.ai.understanding import analyze_input
from jarvis import brain
class TestIntegrationParameterAnalysis(unittest.TestCase):
    def setUp(self):
        self.definition = IntegrationDefinition(
            name="demo",
            description="Integración de prueba",
            version="1.0",
            parameters=[
                IntegrationParameter("expression", "Expresión", str, "-x"),
                IntegrationParameter("precision", "Precisión", int, "--precision", required=False),
            ],
            handler=lambda values: str(values),
        )
        self.handlers = {"demo": self.definition.handler}
        self.definitions = {"demo": self.definition}
    def data(self, text):
        return InputData(text, datetime.now(), "test")
    def test_flags_extract_values_and_convert_types(self):
        result = analyze_input(
            self.data('ejecuta demo -x "hola mundo" --precision 3'),
            available_integrations=self.handlers,
            integration_definitions=self.definitions,
        )
        self.assertEqual(result.entities["parameters"], {"expression": "hola mundo", "precision": 3})
        self.assertEqual(result.entities["missing_parameters"], [])
        self.assertEqual(result.entities["errors"], [])
    def test_required_parameter_is_reported_as_missing(self):
        result = analyze_input(
            self.data("ejecuta demo"),
            available_integrations=self.handlers,
            integration_definitions=self.definitions,
        )
        self.assertEqual(result.entities["missing_parameters"], ["expression"])
        self.assertEqual(create_action_plan(result).actions, [])
    def test_unknown_flag_is_reported(self):
        result = analyze_input(
            self.data("ejecuta demo -z valor -x hola"),
            available_integrations=self.handlers,
            integration_definitions=self.definitions,
        )
        self.assertTrue(any("desconocida" in error for error in result.entities["errors"]))
    def test_invalid_typed_value_is_reported(self):
        result = analyze_input(
            self.data("ejecuta demo -x hola --precision tres"),
            available_integrations=self.handlers,
            integration_definitions=self.definitions,
        )
        self.assertTrue(any("int" in error for error in result.entities["errors"]))
    def test_core_passes_integration_definitions_to_understanding(self):
        core = AICore(self.handlers, integration_definitions=self.definitions)
        analysis, plan = core.process_input(self.data("ejecuta demo -x prueba"))
        self.assertEqual(analysis.entities["parameters"], {"expression": "prueba"})
        self.assertEqual(plan.actions[0].parameters, {"expression": "prueba"})
    def test_reasoning_does_not_create_action_with_missing_parameters(self):
        analysis = AnalysisResult(
            intent="integration",
            entities={"integration": "demo", "parameters": {}, "missing_parameters": ["expression"], "errors": []},
            confidence=1.0,
            understood=True,
        )
        self.assertEqual(create_action_plan(analysis).actions, [])
class TestBrainMissingIntegrationParameters(unittest.TestCase):
    def setUp(self):
        brain._PENDING_PLAN = None
        brain._PENDING_INTEGRATION = None
        brain._PENDING_OPERATION = None
        brain._PENDING_GROUP_SELECTION = None
        brain._PENDING_ACTION_INDEX = 0
    def tearDown(self):
        brain._PENDING_PLAN = None
        brain._PENDING_INTEGRATION = None
        brain._PENDING_OPERATION = None
        brain._PENDING_GROUP_SELECTION = None
        brain._PENDING_ACTION_INDEX = 0
    def test_brain_prompts_for_missing_parameter_then_confirmation(self):
        with (
            patch.object(brain._AI_CORE, "execute_plan") as execute,
            patch.object(
                brain._BACKGROUND_TASKS,
                "submit_task",
                side_effect=lambda task, *args, **kwargs: (
                    task(),
                    "task-1",
                )[1],
            ) as submit,
        ):
            response = brain.process_command("ejecuta calculadora")
            self.assertIn("expresion", response)
            self.assertIsNotNone(brain._PENDING_INTEGRATION)
            response = brain.process_command("2+2")
            self.assertIn("PLAN DE EJECUCIÓN", response)
            self.assertIsNone(brain._PENDING_INTEGRATION)
            execute.assert_not_called()
            response = brain.process_command("S")
            self.assertIn("¿A qué grupo", response)
            execute.assert_not_called()
            response = brain.process_command("1")
            self.assertIn("1 acción(es) enviada(s)", response)
            submit.assert_called_once()
            execute.assert_called_once()
            executed_plan = execute.call_args.args[0]
            self.assertEqual(len(executed_plan.actions), 1)
            self.assertTrue(execute.call_args.kwargs["confirmed"])
    def test_brain_accepts_flags_without_prompting(self):
        with patch.object(brain._AI_CORE, "execute_plan") as execute:
            response = brain.process_command('ejecuta calculadora -x "2+2"')
            self.assertIn("PLAN DE EJECUCIÓN", response)
            self.assertIsNone(brain._PENDING_INTEGRATION)
            execute.assert_not_called()
    def test_brain_can_cancel_parameter_collection(self):
        response = brain.process_command("ejecuta calculadora")
        self.assertIn("expresion", response)
        response = brain.process_command("cancelar")
        self.assertIn("cancelada", response)
        self.assertIsNone(brain._PENDING_INTEGRATION)
if __name__ == "__main__":
    unittest.main()