import click
from rich.console import Console
from rich.panel import Panel
from agentops_ai.agentops_core.services.test_generator import TestGenerator
from agentops_ai.agentops_core.analyzer import CodeAnalyzer, _add_parents, analyze_tree_with_parents
import subprocess
import sys
import ast
import os
import yaml
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from collections import defaultdict
import json
import datetime
from rich import box
import glob
from agentops_ai import agentops_regen_checker

console = Console(file=sys.stdout, force_terminal=False)
USAGE_FILE = os.path.expanduser('~/.agentops_usage.json')

def load_config(directory):
    """
    Load the .agentops.yml config file from the given directory, if it exists.
    Returns a dict of config values or an empty dict if not found or if malformed.
    """
    config_path = os.path.join(directory, '.agentops.yml')
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            if not isinstance(config, dict):
                return {}
            return config
        except Exception:
            return {}
    return {}

def load_usage(usage_file=USAGE_FILE):
    if os.path.exists(usage_file):
        try:
            with open(usage_file) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_usage(data, usage_file=USAGE_FILE):
    try:
        with open(usage_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def log_error(error_msg, log_file=None):
    log_file = log_file or os.path.expanduser('~/.agentops_errors.log')
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] {error_msg}\n")

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
def cli():
    """
    AgentOps - AI-powered testing for everyone.

    Example usage:
      agentops init
      agentops generate mymodule.py
      agentops run --show-coverage
      agentops analyze mymodule.py
    """
    pass

@cli.command(help="Initialize a new AgentOps project. Creates a tests/ directory and a sample .agentops.yml config.\n\nExample: agentops init")
@click.argument('directory', default='.')
def init(directory):
    """
    Initialize a new AgentOps project in the specified directory.
    Creates a tests/ directory and a sample .agentops.yml config file if not present.
    """
    project_dir = os.path.abspath(directory)
    os.makedirs(project_dir, exist_ok=True)
    # Ensure tests directory exists
    tests_dir = os.path.join(project_dir, 'tests')
    if not os.path.exists(tests_dir):
        os.makedirs(tests_dir)
        console.print(Panel(f"Created tests directory at {tests_dir}", title="AgentOps Init", style="green"))
    else:
        console.print(Panel(f"Tests directory already exists at {tests_dir}", title="AgentOps Init", style="yellow"))
    # Ensure config file exists
    config_path = os.path.join(project_dir, '.agentops.yml')
    if not os.path.exists(config_path):
        sample_config = {
            'test_framework': 'pytest',
            'openai_model': 'gpt-4o-mini',
            'test_output_dir': 'tests',
            'coverage': True
        }
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        console.print(Panel(f"Created sample config at {config_path}", title="AgentOps Init", style="green"))
    else:
        console.print(Panel(f"Config already exists at {config_path}", title="AgentOps Init", style="yellow"))
    console.print(Panel(f"AgentOps project initialized at {project_dir}", title="AgentOps Init", style="cyan"))

@cli.command(name="generate", help="Generate tests for a Python file using AI.\n\nExample: agentops generate mymodule.py --framework pytest")
@click.argument('target', default='.')
@click.option('--type', '-t', default=None, help='What to generate (tests, docs, etc.)')
@click.option('--framework', '-f', default=None, help='Testing framework to use (pytest, unittest)')
@click.option('--api-key', default=None, help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--cursor', is_flag=True, help='Output results in Cursor-friendly JSON format')
@click.option('--all', 'all_files', is_flag=True, help='Generate tests for all Python files in the project')
@click.option('--force-generate', is_flag=True, help='Force regeneration of all tests regardless of hash')
@click.option('--api', is_flag=True, help='Generate API endpoint tests for FastAPI/Flask')
def generate(target, type, framework, api_key, cursor, all_files, force_generate, api):
    """
    Generate tests for a Python file using the AI-powered test generator.
    Uses config values from .agentops.yml if present.
    """
    import fnmatch
    def find_py_files(root):
        py_files = []
        for dirpath, dirnames, filenames in os.walk(root):
            print(f"[AgentOps DEBUG] Walking: {dirpath}")
            dirnames[:] = [d for d in dirnames if d not in ('tests', '__pycache__') and not d.startswith('.')]
            for filename in filenames:
                if filename.endswith('.py'):
                    py_files.append(os.path.join(dirpath, filename))
        return py_files
    def get_test_path(py_file):
        rel_path = os.path.relpath(py_file, os.getcwd())
        if rel_path.startswith("./"): rel_path = rel_path[2:]
        if rel_path.startswith("src/"): rel_path = rel_path[4:]
        test_dir = os.path.join(".agentops", "tests", os.path.dirname(rel_path))
        test_file = os.path.join(test_dir, f"test_{os.path.basename(rel_path)}")
        return test_file
    if all_files:
        # Always search from the main source directory
        project_root = os.path.abspath("agentops_ai")
        py_files = find_py_files(project_root)
        click.echo(f"[AgentOps DEBUG] Found {len(py_files)} Python files for test generation:")
        for f in py_files:
            click.echo(f"  - {f}")
        generated = []
        skipped = []
        for file in py_files:
            abs_file = os.path.abspath(file)
            test_path = get_test_path(file)
            if agentops_regen_checker.needs_regeneration(abs_file, test_path, force_generate):
                click.echo(f"[AgentOps] Generating tests for {file}...")
                ctx = click.get_current_context()
                ctx.invoke(generate, target=file, type=type, framework=framework, api_key=api_key, cursor=cursor, all_files=False, force_generate=force_generate, api=api)
                generated.append(file)
                agentops_regen_checker.update_hash(abs_file)
            else:
                skipped.append(file)
        click.echo(f"[AgentOps] Test generation complete for {len(generated)} files.")
        if generated:
            click.echo("\n[AgentOps] Tests generated or regenerated for:")
            for f in generated:
                click.echo(f"  - {f}")
        if skipped:
            click.echo("\n[AgentOps] Skipped (up-to-date):")
            for f in skipped:
                click.echo(f"  - {f}")
        return
    project_dir = os.path.dirname(target) if os.path.isfile(target) else target
    config = load_config(project_dir)
    if config and not cursor:
        console.print(Panel(f"Loaded config from .agentops.yml:\n{config}", title="AgentOps Config", style="cyan"))
    type = type or config.get('type', 'tests')
    framework = framework or config.get('test_framework', 'pytest')
    api_key = api_key or config.get('openai_api_key')
    model = config.get('openai_model', 'gpt-4o-mini')
    if type != 'tests':
        msg = "Only test generation is supported right now. Use --type tests."
        if cursor:
            print(json.dumps({"success": False, "error": msg}))
        else:
            console.print(Panel(f"[red]{msg}[/red]", title="AgentOps Generate", style="red"))
        return
    if not target.endswith('.py'):
        msg = "Currently, only single Python files are supported."
        if cursor:
            print(json.dumps({"success": False, "error": msg}))
        else:
            console.print(Panel(f"[red]{msg}[/red]", title="AgentOps Generate", style="red"))
        return
    try:
        with open(target) as f:
            code = f.read()
    except Exception as e:
        msg = f"Failed to read file: {e}"
        if cursor:
            print(json.dumps({"success": False, "error": msg}))
        else:
            console.print(Panel(f"[red]{msg}[/red]", title="AgentOps Generate", style="red"))
        return
    if not cursor:
        console.print(Panel(f"Generating {framework} tests for {target}...", title="AgentOps Generate", style="cyan"))
    tg = TestGenerator(api_key=api_key, model=model)
    result = tg.generate_tests(code, framework=framework, module_path=target, api_mode=api)
    if not result["success"]:
        if cursor:
            print(json.dumps(result))
        else:
            console.print(Panel(f"[red]Test generation failed: {result['error']}[/red]", title="AgentOps Generate", style="red"))
            log_error(result['error'])
        return
    test_code = result["tests"]
    # Syntax check before writing
    try:
        ast.parse(test_code)
    except Exception as e:
        console.print(Panel(f"[red]Generated test code has syntax errors: {e}[/red]", title="AgentOps Generate", style="red"))
        return
    test_file_path = get_test_path(target)
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    # Ensure __init__.py in each new directory for importability
    test_dir = os.path.dirname(test_file_path)
    parts = test_dir.split(os.sep)
    for i in range(1, len(parts)+1):
        d = os.sep.join(parts[:i])
        init_file = os.path.join(d, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")
    with open(test_file_path, "w") as f:
        f.write(test_code)
    if cursor:
        print(json.dumps({"success": True, "output_file": test_file_path, "confidence": result["confidence"], "tests": test_code}))
    else:
        console.print(Panel(f"[green]Test generation complete![/green]\nSaved to: {test_file_path}\nConfidence: {result['confidence']}", title="AgentOps Generate", style="green"))

@cli.command(name="run", help="Run all tests in the tests/ directory and show results.\n\nExample: agentops run --show-coverage")
@click.argument('target', default='tests')
@click.option('--show-coverage', is_flag=True, help='Show coverage information')
@click.option('--cursor', is_flag=True, help='Output results in Cursor-friendly JSON format')
def run(target, show_coverage, cursor):
    """
    Run all tests in the specified directory (default: tests/) and show results.
    Optionally show coverage information if --show-coverage is passed or enabled in config.
    """
    import sys
    sys.path.insert(0, os.path.abspath('.'))
    config = load_config(target) if os.path.isdir(target) else load_config(os.path.dirname(target))
    if config and not cursor:
        console.print(Panel(f"Loaded config from .agentops.yml:\n{config}", title="AgentOps Config", style="cyan"))
    show_coverage = show_coverage or config.get('coverage', False)
    if not cursor:
        console.print(Panel(f"Running {target}...", title="AgentOps Run", style="cyan"))
    try:
        cov_data = None
        coverage_output = None
        if show_coverage:
            # Run tests with coverage
            result = subprocess.run([sys.executable, '-m', 'coverage', 'run', '-m', 'pytest', target, '--tb=short', '--maxfail=10', '--json-report'], capture_output=True, text=True)
            cov_result = subprocess.run([sys.executable, '-m', 'coverage', 'report', '-m'], capture_output=True, text=True)
            output = result.stdout
            coverage_output = cov_result.stdout
            if not cursor:
                display_coverage_visuals(coverage_output)
            else:
                cov_data = parse_coverage_for_json(coverage_output)
        else:
            # Run tests without coverage
            result = subprocess.run([sys.executable, '-m', 'pytest', target, '--tb=short', '--maxfail=10', '--json-report'], capture_output=True, text=True)
            output = result.stdout
        # Visual test result feedback
        if result.returncode == 0:
            if cursor:
                print(json.dumps({"success": True, "output": output, "coverage": cov_data if show_coverage else None}))
            else:
                console.print(Panel(f"✅ [green]All tests passed![/green]\n\n{output}", title="AgentOps Run", style="green"))
        else:
            if cursor:
                print(json.dumps({"success": False, "output": output, "coverage": cov_data if show_coverage else None}))
            else:
                console.print(Panel(f"❌ [red]Some tests failed.[/red]\n\n{output}", title="AgentOps Run", style="red"))
        # Data collection: usage stats
        if not cursor and config.get('collect_usage', True):
            usage = load_usage()
            usage.setdefault('run_stats', []).append({
                'target': target,
                'success': result.returncode == 0,
                'timestamp': datetime.datetime.now().isoformat()
            })
            save_usage(usage)
        # Rich summary table for vibe coders
        if not cursor:
            try:
                from pathlib import Path
                import json as _json
                report_path = Path(".pytest_cache/lastfailed.json")
                json_report_path = Path(".pytest_cache/v/cache/stepwise.json")
                # Try to find pytest's json report
                json_report = None
                for f in Path(target).glob(".pytest_cache/**/report.json"):
                    json_report = f
                    break
                if json_report and json_report.exists():
                    with open(json_report) as f:
                        report = _json.load(f)
                    table = Table(title="Test Run Summary", box=box.SIMPLE)
                    table.add_column("Test Name", style="cyan")
                    table.add_column("Importance", style="magenta")
                    table.add_column("Confidence", style="green")
                    table.add_column("Result", style="yellow")
                    table.add_column("Regen Flag", style="red")
                    for test in report.get("tests", []):
                        name = test.get("nodeid", "?")
                        importance = test.get("importance", "Routine")
                        confidence = test.get("confidence", "86%")
                        result = "✅ Pass" if test.get("outcome") == "passed" else "❌ Fail"
                        regen = "⚠️" if float(str(confidence).replace('%','')) < 70 else ""
                        table.add_row(name, importance, str(confidence), result, regen)
                    console.print(table)
            except Exception:
                pass
        # Post-failure explainability
        if result.returncode != 0 and not cursor:
            console.print(Panel("[yellow]Some tests failed.\nIf this is a generated test, try regenerating with AgentOps or review the code for recent changes.\nIf confidence < 70%, consider regenerating the test.[/yellow]", title="AgentOps QA Helper", style="yellow"))
    except Exception as e:
        msg = f"Failed to run tests: {e}"
        if cursor:
            print(json.dumps({"success": False, "error": msg}))
        else:
            console.print(Panel(f"[red]{msg}[/red]", title="AgentOps Run", style="red"))
        log_error(msg)

def parse_coverage_for_json(coverage_output):
    """
    Parse coverage report output for JSON output (for Cursor integration).
    """
    lines = coverage_output.strip().split('\n')
    files = []
    total_coverage = None
    for line in lines:
        if line.startswith('Name') or line.startswith('-') or not line.strip():
            continue
        if line.startswith('TOTAL'):
            parts = line.split()
            if len(parts) >= 4:
                total_coverage = int(parts[3].replace('%', ''))
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[2].endswith('%'):
            filename = parts[0]
            stmts = int(parts[1])
            miss = int(parts[2]) if parts[2].isdigit() else 0
            cover = int(parts[3].replace('%', ''))
            files.append({"file": filename, "statements": stmts, "missed": miss, "coverage": cover})
    return {"files": files, "total_coverage": total_coverage}

@cli.command(name="cursor", help="(Stub) Integration point for Cursor AI. Future: direct API integration.")
def cursor():
    """
    Placeholder for Cursor AI integration. In the future, this will enable direct API calls and richer UI feedback.
    """
    console.print(Panel("Cursor integration is coming soon! Use --cursor flag on other commands for now.", title="Cursor Integration", style="cyan"))

@cli.command(name="analyze", help="Analyze code quality and provide suggestions for a Python file.\n\nExample: agentops analyze mymodule.py")
@click.argument('target', default='.')
def analyze(target):
    """
    Analyze code quality and provide suggestions for a Python file.
    Uses AST-based analysis to summarize imports, functions, and classes, and gives suggestions.
    """
    config = load_config(os.path.dirname(target))
    if config:
        console.print(Panel(f"Loaded config from .agentops.yml:\n{config}", title="AgentOps Config", style="cyan"))
    if not target.endswith('.py'):
        console.print(Panel(f"[red]Currently, only single Python files are supported.[/red]", title="AgentOps Analyze", style="red"))
        return
    try:
        with open(target) as f:
            code = f.read()
    except Exception as e:
        console.print(Panel(f"[red]Failed to read file: {e}[/red]", title="AgentOps Analyze", style="red"))
        return
    tree = ast.parse(code)
    _add_parents(tree)
    result = analyze_tree_with_parents(tree)
    summary = []
    summary.append(f"[bold]Imports:[/bold] {', '.join(result['imports']) if result['imports'] else 'None'}")
    summary.append(f"[bold]Functions:[/bold] {', '.join(f.name for f in result['functions']) if result['functions'] else 'None'}")
    summary.append(f"[bold]Classes:[/bold] {', '.join(c.name for c in result['classes']) if result['classes'] else 'None'}")
    suggestions = []
    if not result['functions']:
        suggestions.append("No functions found. Consider adding reusable functions.")
    if not result['classes']:
        suggestions.append("No classes found. Consider using classes for better organization.")
    if not result['imports']:
        suggestions.append("No imports found. Is this file self-contained?")
    console.print(Panel("\n".join(summary), title="Code Summary", style="cyan"))
    if suggestions:
        console.print(Panel("\n".join(suggestions), title="Suggestions", style="yellow"))
    else:
        console.print(Panel("Code looks well-structured!", title="Suggestions", style="green"))

def display_coverage_visuals(coverage_output):
    """
    Parse and display coverage report output visually using Rich.
    """
    from rich.table import Table
    import os
    from collections import defaultdict
    lines = coverage_output.strip().split('\n')
    file_rows = []
    total_coverage = None
    dir_coverage = defaultdict(list)
    for line in lines:
        if line.startswith('Name') or line.startswith('-') or not line.strip():
            continue
        if line.startswith('TOTAL'):
            parts = line.split()
            if len(parts) >= 4:
                total_coverage = int(parts[3].replace('%', ''))
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[2].endswith('%'):
            filename = parts[0]
            stmts = int(parts[1])
            miss = int(parts[2]) if parts[2].isdigit() else 0
            cover = int(parts[3].replace('%', ''))
            file_rows.append((filename, stmts, miss, cover))
            dir_name = os.path.dirname(filename)
            dir_coverage[dir_name].append(cover)
    # Directory-level summary
    table = Table(title="Directory Coverage Summary", show_lines=True)
    table.add_column("Directory", style="cyan")
    table.add_column("Avg Coverage", style="magenta")
    table.add_column("Visual", style="white")
    for dir_name, covers in dir_coverage.items():
        avg_cov = sum(covers) / len(covers)
        bar = get_coverage_bar(avg_cov)
        table.add_row(dir_name or '.', f"{avg_cov:.1f}%", bar)
    console.print(table)
    # Per-file bars
    file_table = Table(title="File Coverage", show_lines=False)
    file_table.add_column("File", style="cyan")
    file_table.add_column("Coverage", style="magenta")
    file_table.add_column("Visual", style="white")
    for filename, stmts, miss, cover in file_rows:
        bar = get_coverage_bar(cover)
        file_table.add_row(filename, f"{cover}%", bar)
    console.print(file_table)
    # Overall summary
    if total_coverage is not None:
        color = "green" if total_coverage >= 90 else "yellow" if total_coverage >= 75 else "red"
        console.print(Panel(f"[bold]{total_coverage}%[/bold] total coverage", title="Overall Coverage", style=color))

def get_coverage_bar(coverage):
    """
    Return a colored bar string for the given coverage percent.
    """
    bar_length = 20
    filled = int(bar_length * coverage / 100)
    empty = bar_length - filled
    color = "green" if coverage >= 90 else "yellow" if coverage >= 75 else "red"
    return f"[bold {color}]{'█'*filled}[/bold {color}]{'░'*empty}"

@cli.command(name="observe", help="Summarize test suite health, coverage, flaky/failing tests, and actionable suggestions.")
def observe():
    test_dir = os.path.join(".agentops", "tests")
    if not os.path.exists(test_dir):
        console.print(Panel("No tests found in .agentops/tests/", title="AgentOps Observe", style="red"))
        return
    test_files = [f for f in glob.glob(os.path.join(test_dir, "**", "test_*.py"), recursive=True) if not f.endswith("__init__.py")]
    if not test_files:
        console.print(Panel("No test files found in .agentops/tests/", title="AgentOps Observe", style="red"))
        return
    total_tests = 0
    failed_tests = 0
    flaky_tests = 0
    coverage = 0.0
    actionable = []
    # Run pytest with coverage and collect results
    import subprocess
    try:
        result = subprocess.run([
            "pytest", test_dir, "--maxfail=10", "--disable-warnings", "--tb=short", "--cov=.", "--cov-report=term-missing", "--json-report", "--json-report-file=.agentops/observe_report.json"
        ], capture_output=True, text=True, check=False)
        output = result.stdout
        if 'pytest_jsonreport.plugin' in result.stderr or 'no such option' in result.stderr:
            console.print(Panel("pytest-json-report is required for observe. Install with: pip install pytest-json-report", title="AgentOps Observe", style="red"))
            return
        # Parse pytest json report
        import json
        report_path = ".agentops/observe_report.json"
        if os.path.exists(report_path):
            with open(report_path) as f:
                report = json.load(f)
            total_tests = report.get("summary", {}).get("total", 0)
            failed_tests = report.get("summary", {}).get("failed", 0)
            # Flaky: look for rerun or xfailed
            flaky_tests = report.get("summary", {}).get("rerun", 0) + report.get("summary", {}).get("xfailed", 0)
        # Parse coverage from output
        for line in output.splitlines():
            if "TOTAL" in line and "%" in line:
                try:
                    coverage = float(line.split()[-1].replace("%", ""))
                except Exception:
                    pass
        if failed_tests > 0:
            actionable.append(f"{failed_tests} test(s) are failing. Investigate and fix them.")
        if coverage < 80.0:
            actionable.append(f"Test coverage is below 80% ({coverage}%). Add more tests.")
        if flaky_tests > 0:
            actionable.append(f"{flaky_tests} flaky or xfailed test(s) detected. Review for stability.")
        if not actionable:
            actionable.append("All tests passing and coverage is healthy. Great job!")
        # Output summary
        console.print(Panel(f"Test files: {len(test_files)}\nTotal tests: {total_tests}\nFailures: {failed_tests}\nFlaky: {flaky_tests}\nCoverage: {coverage}%", title="Test Suite Health", style="cyan"))
        console.print(Panel("\n".join(actionable), title="Actionable Suggestions", style="green" if failed_tests == 0 else "yellow"))
        # Clean up report file
        if os.path.exists(report_path):
            os.remove(report_path)
    except Exception as e:
        console.print(Panel(f"Error running observe: {e}", title="AgentOps Observe", style="red"))

if __name__ == '__main__':
    cli() 