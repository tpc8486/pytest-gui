import argparse
import unittest


class Discover:
    def __init__(self):
        self.tests = []

    @staticmethod
    def flatten_results(iterable):
        """Static method to flatten the nested test suites into a single list of tests."""
        inputs = list(iterable)
        while inputs:
            item = inputs.pop(0)
            try:
                data = iter(item)
                inputs = list(data) + inputs
            except TypeError:
                yield item

    def collect_tests(self, dirname="tests"):
        """Collect all test cases from the specified directory."""
        loader = unittest.TestLoader()
        suite = loader.discover(dirname)
        flat_results = list(self.flatten_results(suite))
        self.tests = [test.id() for test in flat_results]

    def print_tests(self):
        """Prints the list of test case IDs."""
        if self.tests:
            print("\n".join(self.tests))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover and list test cases.")
    parser.add_argument(
        "--testdir",
        dest="testdir",
        default="tests",  # Default directory set to "tests"
        help="Directory to search for test cases.",
    )
    options = parser.parse_args()

    discoverer = Discover()
    discoverer.collect_tests(options.testdir)
    discoverer.print_tests()
