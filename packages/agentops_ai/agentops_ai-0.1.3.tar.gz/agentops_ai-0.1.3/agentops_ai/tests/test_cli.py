import pytest
from click.testing import CliRunner
from agentops_ai.agentops_cli.main import cli, load_config, log_error, load_usage, save_usage
import sys
import tempfile
import os
import yaml
import io
from datetime import datetime
from freezegun import freeze_time

@pytest.fixture
def mock_subprocess_run(monkeypatch):
    class Result:
        def __init__(self, returncode=0, stdout="TEST OUTPUT\n"):
            self.returncode = returncode
            self.stdout = stdout
    def fake_run(*args, **kwargs):
        if '-m' in args[0] and 'coverage' in args[0]:
            return Result(stdout="COVERAGE REPORT\n")
        return Result(stdout="PYTEST OUTPUT\n")
    monkeypatch.setattr(sys.modules['subprocess'], 'run', fake_run)
    return fake_run

def test_run_command_basic(mock_subprocess_run):
    runner = CliRunner()
    import agentops_ai.agentops_cli.main as cli_main
    buf = io.StringIO()
    cli_main.console = cli_main.Console(file=buf, force_terminal=False)
    result = runner.invoke(cli, ['run', 'tests'])
    output = buf.getvalue()
    assert result.exit_code == 0
    assert "AgentOps Run" in output

def test_run_command_coverage():
    runner = CliRunner()
    import agentops_ai.agentops_cli.main as cli_main
    buf = io.StringIO()
    cli_main.console = cli_main.Console(file=buf, force_terminal=False)
    # Simulate a realistic coverage report output
    coverage_report = '''\
Name                                                   Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------
agentops_ai/agentops_cli/main.py                         100     10    90%   10-20
agentops_ai/agentops_core/analyzer.py                    50      5    90%   5-10
------------------------------------------------------------------------------------
TOTAL                                                    150     15    90%
'''
    def fake_run(args, **kwargs):
        class Result:
            def __init__(self, returncode=0, stdout=""):
                self.returncode = returncode
                self.stdout = stdout
        # Simulate 'coverage run -m pytest' call
        if 'coverage' in args and 'run' in args:
            return Result(returncode=0, stdout="PYTEST OUTPUT\n")
        # Simulate 'coverage report -m' call
        if 'coverage' in args and 'report' in args:
            return Result(returncode=0, stdout=coverage_report)
        # Simulate 'pytest' call
        if 'pytest' in args:
            return Result(returncode=0, stdout="PYTEST OUTPUT\n")
        return Result(returncode=0, stdout="")
    import subprocess as _subprocess
    orig_run = _subprocess.run
    _subprocess.run = fake_run
    try:
        result = runner.invoke(cli, ['run', 'tests', '--show-coverage'])
        output = buf.getvalue()
        if "Directory Coverage Summary" not in output:
            print("DEBUG OUTPUT:\n", output)
        assert result.exit_code == 0
        # Check for visual feedback elements
        assert "Directory Coverage Summary" in output
        assert "File Coverage" in output
        assert "Overall Coverage" in output
        assert "90%" in output  # Coverage percentage should always be present
    finally:
        _subprocess.run = orig_run

def test_analyze_command():
    runner = CliRunner()
    import agentops_ai.agentops_cli.main as cli_main
    buf = io.StringIO()
    cli_main.console = cli_main.Console(file=buf, force_terminal=False)
    code = """
import os

def foo(x):
    return x + 1

class Bar:
    def method(self, y):
        return y
"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp.flush()
        result = runner.invoke(cli, ['analyze', tmp.name])
    output = buf.getvalue()
    assert result.exit_code == 0
    assert "Code Summary" in output
    assert "Suggestions" in output
    assert "foo" in output
    assert "Bar" in output

def test_init_command_creates_structure():
    runner = CliRunner()
    import agentops_ai.agentops_cli.main as cli_main
    buf = io.StringIO()
    cli_main.console = cli_main.Console(file=buf, force_terminal=False)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(cli, ['init', tmpdir])
        tests_dir = os.path.join(tmpdir, 'tests')
        config_path = os.path.join(tmpdir, '.agentops.yml')
        assert os.path.isdir(tests_dir)
        assert os.path.isfile(config_path)
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config['test_framework'] == 'pytest'
        assert config['openai_model'] == 'gpt-4o-mini'
        assert config['test_output_dir'] == 'tests'
        assert config['coverage'] is True
        output = buf.getvalue()
        assert "AgentOps project initialized" in output

def test_generate_uses_config(monkeypatch):
    runner = CliRunner()
    import agentops_ai.agentops_cli.main as cli_main
    buf = io.StringIO()
    cli_main.console = cli_main.Console(file=buf, force_terminal=False)
    code = "def foo(x):\n    return x + 1"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write a config file
        config = {
            'test_framework': 'pytest',
            'openai_model': 'gpt-4o-mini',
            'test_output_dir': 'tests',
            'coverage': True,
            'type': 'tests',
            'openai_api_key': 'sk-test'
        }
        config_path = os.path.join(tmpdir, '.agentops.yml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        # Write a code file
        code_path = os.path.join(tmpdir, 'foo.py')
        with open(code_path, 'w') as f:
            f.write(code)
        # Patch TestGenerator to avoid OpenAI call
        monkeypatch.setattr('agentops_ai.agentops_core.services.test_generator.TestGenerator.generate_tests', lambda self, code, framework, module_path=None, api_mode=False: {"success": True, "tests": "# test code", "confidence": 1.0})
        monkeypatch.setattr('agentops_ai.agentops_core.services.test_generator.TestGenerator.write_tests_to_file', lambda self, test_code, output_dir, base_name: os.path.join(output_dir, base_name))
        result = runner.invoke(cli, ['generate', code_path])
        output = buf.getvalue()
        assert result.exit_code == 0
        assert "AgentOps Generate" in output

def test_load_config_returns_empty_dict_if_no_config(tmp_path):
    result = load_config(tmp_path)
    assert result == {}, f"Expected empty dict when no config file, got {result}"

def test_load_config_reads_valid_yaml(tmp_path):
    config = {"foo": "bar", "baz": 123}
    config_path = tmp_path / ".agentops.yml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    result = load_config(tmp_path)
    assert result == config, f"Expected {config}, got {result}"

def test_load_config_returns_empty_dict_on_malformed_yaml(tmp_path):
    config_path = tmp_path / ".agentops.yml"
    config_path.write_text("not: [valid: yaml")
    result = load_config(tmp_path)
    assert result == {}, "Should return empty dict on malformed config"

def test_load_config_returns_empty_dict_on_non_dict_yaml(tmp_path):
    config_path = tmp_path / ".agentops.yml"
    config_path.write_text("- just\n- a\n- list")
    result = load_config(tmp_path)
    assert result == {}, "Should return empty dict on non-dict YAML"

@freeze_time("2025-05-24 12:00:00")
def test_log_error_with_frozen_time(tmp_path):
    log_file = tmp_path / "test_log.log"
    error_msg = "Simulated error"
    log_error(error_msg, log_file=str(log_file))
    with open(log_file, "r") as f:
        lines = f.readlines()
    t_stamp, msg = lines[-1].strip().split("] ")
    assert msg == error_msg
    assert "2025-05-24 12:00:00" in t_stamp

def test_load_config_permission_error(tmp_path, monkeypatch):
    config_path = tmp_path / ".agentops.yml"
    config_path.write_text("test: value")
    def raise_permission(*args, **kwargs):
        raise PermissionError("No permission")
    monkeypatch.setattr("builtins.open", raise_permission)
    result = load_config(tmp_path)
    assert result == {}, "Should return empty dict on permission error"

def test_load_usage_returns_empty_on_missing_file(tmp_path):
    usage_file = tmp_path / "usage.json"
    result = load_usage(usage_file=str(usage_file))
    assert result == {}, "Should return empty dict if usage file missing"

def test_save_and_load_usage(tmp_path):
    usage_file = tmp_path / "usage.json"
    data = {"foo": 1}
    save_usage(data, usage_file=str(usage_file))
    loaded = load_usage(usage_file=str(usage_file))
    assert loaded == data

def test_load_usage_returns_empty_on_malformed_json(tmp_path):
    usage_file = tmp_path / "usage.json"
    usage_file.write_text("not valid json")
    result = load_usage(usage_file=str(usage_file))
    assert result == {}, "Should return empty dict on malformed JSON" 