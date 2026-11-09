import subprocess
import sys
def run_tests() -> None:
    """Ejecuta todas las pruebas de JARVIS."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        check=False,
    )
    raise SystemExit(result.returncode)