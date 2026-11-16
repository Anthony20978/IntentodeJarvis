import subprocess
import sys
def run_tests() -> None:
    """Ejecuta todas las pruebas de JARVIS."""
    test_directories = [
        "tests",
        "src/jarvis/ai/integrations",
    ]
    for directory in test_directories:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                directory,
                "-p",
                "test*.py",
                "-v",
            ],
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)