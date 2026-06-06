import unittest
from django.utils.module_loading import import_string
from django.db import transaction

class AtomicTestResult(unittest.TestResult):
    """
    A TestResult collector that wraps each test execution inside a database 
    transaction block to ensure no test pollution occurs in the database.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
        self.failures_dict = {}

    def get_test_id(self, test):
        if test is None:
            return "unknown.test"
        method_name = getattr(test, '_testMethodName', None)
        if method_name:
            return f"{test.__class__.__name__}.{method_name}"
        return f"{test.__class__.__name__}.{str(test)}"

    def startTest(self, test):
        super().startTest(test)
        self.sid = transaction.savepoint()

    def stopTest(self, test):
        transaction.savepoint_rollback(self.sid)
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(self.get_test_id(test))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_id = self.get_test_id(test)
        self.failures_dict[test_id] = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        test_id = self.get_test_id(test)
        self.failures_dict[test_id] = self._exc_info_to_string(err, test)


def run_koan_tests():
    # Define koans targets
    koans_list = [
        {
            "id": "k01_data_minimization",
            "name": "Data Minimization (Pasal 16)",
            "test_class": "koans.k01_data_minimization.tests.DataMinimizationTestCase"
        },
        {
            "id": "k02_explicit_consent",
            "name": "Explicit Consent (Pasal 20)",
            "test_class": "koans.k02_explicit_consent.tests.ExplicitConsentTestCase"
        },
        {
            "id": "k03_data_security",
            "name": "Data Security (Pasal 39 / ISO 27001)",
            "test_class": "koans.k03_data_security.tests.DataSecurityTestCase"
        }
    ]

    results_summary = []
    total_passed = 0
    total_failed = 0

    loader = unittest.TestLoader()

    for koan in koans_list:
        koan_id = koan["id"]
        koan_name = koan["name"]
        test_class_path = koan["test_class"]
        
        passed_tests = []
        failed_tests = []

        try:
            test_class = import_string(test_class_path)
            suite = loader.loadTestsFromTestCase(test_class)
            
            # Helper to recursively extract individual tests
            flat_tests = []
            def extract_tests(suite_or_test):
                if hasattr(suite_or_test, '_tests'):
                    for item in suite_or_test._tests:
                        extract_tests(item)
                else:
                    if suite_or_test is not None:
                        flat_tests.append(suite_or_test)
                        
            extract_tests(suite)

            # Run the suite for this specific koan
            result = AtomicTestResult()
            with transaction.atomic():
                suite.run(result)
            
            for test in flat_tests:
                test_id = result.get_test_id(test)
                method_name = getattr(test, '_testMethodName', 'test')
                test_desc = test.shortDescription() or method_name
                
                if test_id in result.successes:
                    passed_tests.append({"name": test_desc, "status": "PASSED"})
                    total_passed += 1
                else:
                    error_msg = result.failures_dict.get(test_id, "Test failed")
                    short_error = error_msg.split('\n')[-2] if len(error_msg.split('\n')) > 1 else error_msg
                    failed_tests.append({
                        "name": test_desc,
                        "status": "FAILED",
                        "error": short_error.strip()
                    })
                    total_failed += 1
                    
        except Exception as e:
            # If importing or running class fails, treat all as failed/unimplemented
            failed_tests.append({
                "name": "Module configuration check",
                "status": "FAILED",
                "error": f"Could not load or run tests: {str(e)}"
            })
            total_failed += 1

        status = "COMPLETED" if len(failed_tests) == 0 and len(passed_tests) > 0 else "INCOMPLETE"
        results_summary.append({
            "id": koan_id,
            "name": koan_name,
            "status": status,
            "passed_count": len(passed_tests),
            "failed_count": len(failed_tests),
            "passed": passed_tests,
            "failed": failed_tests
        })

    total_tests = total_passed + total_failed
    progress_percentage = round((total_passed / total_tests) * 100, 1) if total_tests > 0 else 0.0

    return {
        "total_koans": len(koans_list),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "progress_percentage": progress_percentage,
        "details": results_summary
    }
