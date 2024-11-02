from lingu import Test
from .logic import logic, log

class OS_Apps_(Test):
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.delay = 0.2
        self.fast_test = True
        if self.fast_test:
            self.delay = 0

    def request(self, text):
        answer = self.user(text, self.delay)
        log.inf(f"User: {text}")
        log.inf(f"Assistant: {answer}")
        return answer

    def test_execution(self):
        if self.fast_test:
            self.trigger("test", "skip_tts")

        answer = self.request("Hey, open a calculator.")
        log.inf(f"Assistant: {answer}")
        was_opened = logic.validate_if_app_was_opened("calculator")
        if not was_opened:
            log.err("Calculator was not opened")
        self.test_results.append({"success": was_opened, "message": "Calculator was not opened"})

    def execute(self):
        log.inf("Starting OS Apps Test Suite...")
        self.test_execution()
        
        # log.inf test results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        log.inf("\nTest Results:")
        log.inf(f"Total tests: {total_tests}")
        log.inf(f"Passed tests: {passed_tests}")
        log.inf(f"Failed tests: {total_tests - passed_tests}")
        
        log.inf("\nDetailed Results:")
        for i, result in enumerate(self.test_results, 1):
            status = "PASSED" if result["success"] else "FAILED"
            log.inf(f"{i}. [{status}] {result['message']}")

        if passed_tests == total_tests:
            log.inf("\nAll tests passed successfully!")
        else:
            log.inf(f"\n{total_tests - passed_tests} tests failed. Please review the detailed results above.")