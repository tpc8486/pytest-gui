import json
import sys
import time
import traceback
import unittest
from io import StringIO
from libs.constants import DEFAULT_TEST_DIR


class PipedTestResult(unittest.result.TestResult):
    """A test result class that can print test results in a machine-parseable format."""

    RESULT_SEPARATOR = "\x1f"  # ASCII US (Unit Separator)

    def __init__(self, stream, use_old_discovery=True):
        super().__init__()
        self.stream = stream
        self.use_old_discovery = use_old_discovery
        self._first = True

        # Create a clean buffer for stdout content
        self._stdout = StringIO()
        self._current_test = None

    @staticmethod
    def _trim_docstring(docstring):
        """Trim the docstring to remove leading/trailing whitespace and indentation."""
        lines = docstring.expandtabs().splitlines()

        # Calculate the minimum indentation level for all non-empty lines except the first one
        if not lines:
            return ""

        indent = min(
            (len(line) - len(line.lstrip()))
            for line in lines[1:]
            if line.strip()
        ) if lines[1:] else 0

        trimmed = [lines[0].strip()]
        if indent > 0:
            trimmed.extend(line[indent:].rstrip() for line in lines[1:])

        # Strip off trailing and leading blank lines
        trimmed = [line for line in trimmed if line]

        return "\n".join(trimmed)

    def description(self, test):
        """Get a trimmed description of the test."""
        try:
            return self._trim_docstring(test.description)
        except AttributeError:
            return self._trim_docstring(test._testMethodDoc) if test._testMethodDoc else "No description"

    def _write_result(self, status, test, error=None):
        """Write a test result to the stream in JSON format."""
        body = {
            "status": status,
            "end_time": time.time(),
            "description": self.description(test),
            "output": self._stdout.getvalue(),
        }
        if error:
            body["error"] = "\n".join(traceback.format_exception(*error))
        self.stream.write(f"{json.dumps(body)}\n")
        self.stream.flush()
        self._current_test = None

    def startTest(self, test):
        super().startTest(test)
        self._current_test = test
        self._stdout = StringIO()
        sys.stdout = self._stdout

        path = self._get_test_path(test)
        body = {"path": path, "start_time": time.time()}
        if self._first:
            self.stream.write(f"{PipedTestRunner.START_TEST_RESULTS}\n")
            self._first = False
        else:
            self.stream.write(f"{self.RESULT_SEPARATOR}\n")
        self.stream.write(f"{json.dumps(body)}\n")
        self.stream.flush()

    def _get_test_path(self, test):
        if self.use_old_discovery:
            parts = test.id().split(".")
            tests_index = parts.index(DEFAULT_TEST_DIR)
            return f"{parts[tests_index - 1]}.{parts[-2]}.{parts[-1]}"
        return test.id()

    def addSuccess(self, test):
        super().addSuccess(test)
        self._write_result("OK", test)

    def addError(self, test, err):
        if self._current_test is None:
            self.startTest(test)
        super().addError(test, err)
        self._write_result("E", test, err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._write_result("F", test, err)

    def addSubTest(self, test, subtest, err):
        if err is None:
            self._write_result("OK", test)
        elif issubclass(err[0], test.failureException):
            self._write_result("F", test, err)
        else:
            self._write_result("E", test, err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        body = {
            "status": "s",
            "end_time": time.time(),
            "description": self.description(test),
            "error": reason,
            "output": self._stdout.getvalue(),
        }
        self.stream.write(f"{json.dumps(body)}\n")
        self.stream.flush()
        self._current_test = None

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._write_result("x", test, err)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        body = {
            "status": "u",
            "end_time": time.time(),
            "description": self.description(test),
            "output": self._stdout.getvalue(),
        }
        self.stream.write(f"{json.dumps(body)}\n")
        self.stream.flush()
        self._current_test = None


class PipedTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in a machine-parseable format."""

    START_TEST_RESULTS = "\x02"  # ASCII STX (Start of Text)
    END_TEST_RESULTS = "\x03"    # ASCII ETX (End of Text)

    def __init__(self, stream=sys.stdout, use_old_discovery=False):
        super().__init__(stream=stream)
        self.use_old_discovery = use_old_discovery

    def run(self, test):
        """Run the given test case or test suite."""
        old_stdout = sys.stdout
        result = PipedTestResult(self.stream, self.use_old_discovery)
        test(result)
        self.stream.write(f"{self.END_TEST_RESULTS}\n")
        self.stream.flush()
        sys.stdout = old_stdout
        return result
