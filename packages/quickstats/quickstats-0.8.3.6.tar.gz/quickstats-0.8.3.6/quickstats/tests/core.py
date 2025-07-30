import unittest

from quickstats.tests import (
    test_binning,
    test_version,
    test_workspace_config,
    test_flexible_dumper
)

test_registry = {
    "binning": test_binning,
    "version": test_binning,
    "workspace_config": test_workspace_config,
    'flexible_dumper': test_flexible_dumper
}

class DetailedTestResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.stream.write(f"Starting {self.testsRun} / {self.test_case_count}: {self.getDescription(test)}\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write(f"Success: {self.getDescription(test)}\n")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.write(f"Error: {self.getDescription(test)}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.write(f"Failure: {self.getDescription(test)}\n")

class DetailedTestRunner(unittest.TextTestRunner):
    resultclass = DetailedTestResult

    def run(self, test):
        # Count the total number of test cases
        self.resultclass.test_case_count = test.countTestCases()
        return super().run(test)

def run_tests(registry_names=None):
    """
    Run selected unit tests by registry names.

    Parameters
    ----------
    registry_names : list of str, optional
        List of registry names to run. If None, run all tests.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Determine which test modules to load
    if registry_names is None:
        # Run all tests if no specific names are provided
        registry_names = test_registry.keys()
    
    # Load tests from the specified test modules
    for name in registry_names:
        if name in test_registry:
            print(f"Running tests for {name}:")
            suite.addTests(loader.loadTestsFromModule(test_registry[name]))
        else:
            print(f"Warning: '{name}' is not a valid test module name.")
    
    runner = DetailedTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_tests()
