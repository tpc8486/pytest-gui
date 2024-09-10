import argparse
import unittest

from libs.constants import DEFAULT_TEST_DIR


class Discover:
    def __init__(self):
        self.tests = []

    @staticmethod
    def flatten_results(iterable):
        """Flatten the nested test suites into a single list of tests."""
        stack = list(iterable)
        while stack:
            item = stack.pop(0)
            try:
                # If item is iterable, extend stack with its contents
                stack.extend(iter(item))
            except TypeError:
                # If item is not iterable, yield it
                yield item

    def collect_tests(self, dirname=DEFAULT_TEST_DIR):
        """Collect all test cases from the specified directory."""
        loader = unittest.TestLoader()
        suite = loader.discover(dirname)
        flat_results = list(self.flatten_results(suite))
        self.tests = [test.id() for test in flat_results]

    def print_tests(self):
        """Print the list of test case IDs."""
        if self.tests:
            print("\n".join(self.tests))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover and list test cases.")
    parser.add_argument(
        "--testdir",
        dest="testdir",
        default=DEFAULT_TEST_DIR,
        help="Directory to search for test cases.",
    )
    options = parser.parse_args()

    discoverer = Discover()
    discoverer.collect_tests(options.testdir)
    discoverer.print_tests()
