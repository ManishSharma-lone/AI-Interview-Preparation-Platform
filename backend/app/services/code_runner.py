import os
import sys
import json
import tempfile
import subprocess
import time
import re
from typing import List, Dict, Any
from backend.app.schemas.api_schemas import CodeRunResult, TestCaseResult

class CodeRunner:
    # Set of blacklisted keywords/modules to prevent malicious actions
    BLACKLIST = [
        r"\bos\b", r"\bsys\b", r"\bsubprocess\b", r"\bshutil\b", r"\bsocket\b",
        r"\bimportlib\b", r"\bbuiltins\b", r"\bopen\b", r"\bwrite\b", r"\bread\b",
        r"__import__", r"\beval\b", r"\bexec\b", r"\bgetattr\b", r"\bsetattr\b",
        r"\bdelattr\b", r"\bglob\b", r"\bpty\b", r"\bplatform\b", r"\bthreading\b"
    ]

    @classmethod
    def check_security(cls, code: str) -> (bool, str):
        """Scans candidate code for unauthorized keyword/import patterns."""
        for pattern in cls.BLACKLIST:
            if re.search(pattern, code):
                # Clean name for error reporting
                clean_name = pattern.replace(r"\b", "").replace(r"(", "")
                return False, f"Security Violation: Use of '{clean_name}' is restricted in this sandboxed environment."
        return True, ""

    @classmethod
    def run_code(cls, code: str, test_cases_json: str, language: str = "python") -> CodeRunResult:
        if language and language.lower() != "python":
            try:
                test_cases = json.loads(test_cases_json)
            except Exception:
                test_cases = []
            return CodeRunResult(
                success=True,
                stdout=f"Local sandbox compilation is not supported for {language.upper()}.\nOnly Python 3 execution is supported.",
                stderr="",
                run_time=0.0,
                memory_usage=0.0,
                passed_count=0,
                total_count=len(test_cases),
                results=[TestCaseResult(
                    name=tc.get("name", f"Test Case {idx+1}"),
                    passed=False,
                    input=tc.get("input", ""),
                    expected=tc.get("expected", ""),
                    actual="",
                    error=f"Live execution not supported for {language.capitalize()}"
                ) for idx, tc in enumerate(test_cases)]
            )
        return cls.run_python_code(code, test_cases_json)

    @classmethod
    def run_python_code(cls, code: str, test_cases_json: str) -> CodeRunResult:
        """Executes candidate code against test cases in a timed subprocess and parses results."""
        # 1. Security Check
        is_safe, error_msg = cls.check_security(code)
        if not is_safe:
            return CodeRunResult(
                success=False,
                stdout="",
                stderr=error_msg,
                run_time=0.0,
                memory_usage=0.0,
                passed_count=0,
                total_count=0,
                results=[]
            )

        # Parse test cases
        try:
            test_cases = json.loads(test_cases_json)
        except Exception:
            return CodeRunResult(
                success=False,
                stdout="",
                stderr="Invalid test cases database configuration.",
                run_time=0.0,
                memory_usage=0.0,
                passed_count=0,
                total_count=0,
                results=[]
            )

        # 2. Prepare Sandbox Execution Code
        # We inject a test driver into the temporary script.
        # The script defines the student's code, runs the test cases, and outputs a JSON result.
        driver_code = f"""
import json
import time
import sys

# Candidate Code
{code}

# Test Cases Data
test_cases_list = {json.dumps(test_cases)}
test_results = []

for idx, tc in enumerate(test_cases_list):
    name = tc.get("name", f"Test Case {{idx+1}}")
    input_str = tc.get("input", "")
    expected_str = tc.get("expected", "")

    try:
        # Parse inputs. E.g. "'hello'" -> "hello" or "2, 3" -> tuple(2, 3)
        # We evaluate input inside a safe namespace
        local_env = {{}}
        # Define candidate functions in the local env
        for k, v in list(globals().items()):
            local_env[k] = v

        # Evaluate the input arguments
        args = eval(f"({{input_str}},)", local_env)
        
        # Identify candidate function
        candidate_func = None
        for key, val in list(globals().items()):
            if callable(val) and key not in ["json", "time", "sys", "test_cases_list", "test_results", "tc", "idx", "name", "input_str", "expected_str"]:
                if f"def {{key}}" in {repr(code)}:
                    candidate_func = val
                    break

        if not candidate_func:
            raise Exception("No user-defined function found in the code submission.")

        start_t = time.perf_counter()
        actual_val = candidate_func(*args)
        end_t = time.perf_counter()
        
        expected_val = eval(expected_str, local_env)
        
        passed = (actual_val == expected_val)

        test_results.append({{
            "name": name,
            "passed": passed,
            "input": input_str,
            "expected": str(expected_val),
            "actual": str(actual_val),
            "error": None
        }})

    except Exception as e:
        test_results.append({{
            "name": name,
            "passed": False,
            "input": input_str,
            "expected": expected_str,
            "actual": "",
            "error": str(e)
        }})

# Output results to stdout as JSON
print("===JSON_START===")
print(json.dumps(test_results))
print("===JSON_END===")
"""

        # 3. Write temp file and run subprocess
        temp_file_path = None
        try:
            fd, temp_file_path = tempfile.mkstemp(suffix=".py", text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(driver_code)

            start_exec = time.perf_counter()
            # Run using the system's python executable
            process = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=3.0 # 3 second timeout limit
            )
            end_exec = time.perf_counter()
            run_time = round((end_exec - start_exec) * 1000.0, 2) # in ms

            stdout = process.stdout
            stderr = process.stderr

            if process.returncode != 0:
                # Execution error
                return CodeRunResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr or f"Execution failed with return code {process.returncode}.",
                    run_time=run_time,
                    memory_usage=0.0,
                    passed_count=0,
                    total_count=len(test_cases),
                    results=[TestCaseResult(name=tc.get("name", "Test Case"), passed=False, input=tc.get("input", ""), expected=tc.get("expected", ""), actual="", error=stderr) for tc in test_cases]
                )

            # Extract JSON output from driver execution
            json_match = re.search(r"===JSON_START===\n(.*)\n===JSON_END===", stdout, re.DOTALL)
            if json_match:
                parsed_results = json.loads(json_match.group(1))
                passed_count = sum(1 for r in parsed_results if r["passed"])
                
                # Standardize results to TestCaseResult
                results_list = []
                for pr in parsed_results:
                    results_list.append(TestCaseResult(
                        name=pr["name"],
                        passed=pr["passed"],
                        input=pr["input"],
                        expected=pr["expected"],
                        actual=pr["actual"],
                        error=pr["error"]
                    ))

                # Extract stdout outside JSON tags
                clean_stdout = stdout.replace("===JSON_START===", "").replace("===JSON_END===", "").replace(json_match.group(1), "").strip()

                return CodeRunResult(
                    success=True,
                    stdout=clean_stdout,
                    stderr="",
                    run_time=run_time,
                    memory_usage=0.1,  # SQLite sandbox simulated memory
                    passed_count=passed_count,
                    total_count=len(test_cases),
                    results=results_list
                )
            else:
                return CodeRunResult(
                    success=False,
                    stdout=stdout,
                    stderr="Failed to parse test case outputs from execution stream.",
                    run_time=run_time,
                    memory_usage=0.0,
                    passed_count=0,
                    total_count=len(test_cases),
                    results=[]
                )

        except subprocess.TimeoutExpired:
            return CodeRunResult(
                success=False,
                stdout="",
                stderr="Execution Error: Time Limit Exceeded (3.0 seconds). Check for infinite loops in your code.",
                run_time=3000.0,
                memory_usage=0.0,
                passed_count=0,
                total_count=len(test_cases),
                results=[]
            )
        except Exception as e:
            return CodeRunResult(
                success=False,
                stdout="",
                stderr=f"Runtime error setting up execution context: {str(e)}",
                run_time=0.0,
                memory_usage=0.0,
                passed_count=0,
                total_count=len(test_cases),
                results=[]
            )
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
