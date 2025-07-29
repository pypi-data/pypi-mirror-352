import subprocess
import sys
from pathlib import Path

CLI_PATH = Path(__file__).resolve().parents[1] / "ifcdate" / "cli.py"

def run_cli(*args):
    # Run CLI as a module to maintain package context and support relative imports
    return subprocess.run(
        [sys.executable, "-m", "ifcdate.cli", *args],
        capture_output=True,
        text=True,
    )

def test_cli_default_runs():
    result = run_cli()
    assert result.returncode == 0
    assert "@" in result.stdout or "Error" not in result.stdout

def test_cli_with_unix_timestamp():
    result = run_cli("-u", "0")
    assert result.returncode == 0
    # unix_to_ifc(0) returns '1970-01-01' (no @)
    assert result.stdout.strip() == "1970-01-01"

def test_cli_verbose_with_date():
    result = run_cli("-d", "2025-01-01", "-v")
    assert result.returncode == 0
    assert "Gregorian Date" in result.stdout
    assert "IFC Date" in result.stdout

def test_cli_with_ifc_date():
    result = run_cli("-i", "2025-01-01")
    assert result.returncode == 0
    assert "2025-01-01" in result.stdout
