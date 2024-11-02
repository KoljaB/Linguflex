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

    # def validate(self, word, message):
    #     # condition = logic.memory.find_by_words(word.lower())
    #     self.test_results.append({"success": condition is not None, "message": message})

    def test_execution(self):
        # Clear the memory before starting tests
        if self.fast_test:
            self.trigger("test", "skip_tts")

        # Test 1: Basic name introduction
        answer = self.request("Hey, open a calculator.")
        log.inf(f"Assistant: {answer}")
        was_opened = logic.validate_if_app_was_opened("calculator")
        if not was_opened:
            log.err("Calculator was not opened")
        self.test_results.append({"success": was_opened, "message": "Calculator was not opened"})

        # # Test 2: Age and occupation information
        # self.request("I'm 28 years old and work as a software engineer.")
        # self.validate("28", "Age should be stored")
        # self.validate("software", "Occupation keyword should be stored")
        # self.validate("engineer", "Occupation keyword should be stored")

        # # Test 3: Hobby information
        # self.request("I love playing tennis on weekends and reading science fiction books.")
        # self.validate("tennis", "Hobby (tennis) should be stored")
        # self.validate("fiction", "Book genre should be stored")

        # # Test 4: Pet information
        # self.request("I have a 3-year-old golden retriever named Max.")
        # self.validate("retriever", "Pet breed should be stored")
        # self.validate("max", "Pet name should be stored")

        # # Test 5: Location information
        # self.request("I've been living in New York City for the past 5 years.")
        # self.validate("york", "City name should be stored")

        # # Test 6: Family information
        # self.request("I have two sisters, Emma and Olivia, and a younger brother named Ethan.")
        # self.validate("sisters", "Family relation should be stored")
        # self.validate("emma", "Sister's name should be stored")
        # self.validate("olivia", "Sister's name should be stored")
        # self.validate("brother", "Family relation should be stored")
        # self.validate("ethan", "Brother's name should be stored")

        # # Test 7: Education information
        # self.request("I graduated from MIT with a degree in Computer Science.")
        # self.validate("mit", "University name should be stored")
        # self.validate("computer", "Degree subject should be stored")

        # # Test 8: Language skills
        # self.request("I'm fluent in English and Spanish, and I'm learning Japanese.")
        # self.validate("english", "Known language should be stored")
        # self.validate("spanish", "Known language should be stored")
        # self.validate("japanese", "Language being learned should be stored")

        # # Test 9: Travel experience
        # self.request("Last summer, I backpacked through Europe, visiting 10 countries in 2 months.")
        # self.validate("europe", "Travel destination should be stored")
        # self.validate("10", "Number of countries visited should be stored")

        # # Test 10: Food preferences
        # self.request("I'm a vegetarian and I love spicy Thai food.")
        # self.validate("vegetarian", "Dietary preference should be stored")
        # self.validate("thai", "Favorite cuisine should be stored")

        # # Test 11: Musical taste
        # self.request("I play the guitar and I'm a big fan of classic rock bands like Led Zeppelin and Pink Floyd.")
        # self.validate("guitar", "Musical instrument should be stored")
        # self.validate("zeppelin", "Favorite band should be stored")
        # self.validate("floyd", "Favorite band should be stored")

        # # Test 12: Career goals
        # self.request("My career goal is to become a senior software architect in the next five years.")
        # self.validate("architect", "Career goal keyword should be stored")

        # # Test 13: Favorite movie
        # self.request("My all-time favorite movie is The Shawshank Redemption.")
        # self.validate("redemption", "Favorite movie should be stored")

        # # Test 14: Phobia
        # self.request("I have a fear of heights, so I avoid tall buildings and roller coasters.")
        # self.validate("heights", "Phobia should be stored")

        # # Test 15: Recent achievement
        # self.request("I recently ran my first marathon in 4 hours and 30 minutes.")
        # self.validate("marathon", "Achievement should be stored")

        # # Test 16: Childhood memory
        # self.request("I grew up in a small town in Texas and spent summers on my grandparents' farm.")
        # self.validate("texas", "Childhood location should be stored")
        # self.validate("farm", "Childhood memory keyword should be stored")

        # # Test 17: Future plans
        # self.request("I'm planning to start my own tech startup in the next two years.")
        # self.validate("startup", "Future plan keyword should be stored")

        # # Test 18: Favorite book
        # self.request("My favorite book is '1984' by George Orwell. I've read it at least five times.")
        # self.validate("1984", "Favorite book should be stored")
        # self.validate("orwell", "Favorite author should be stored")

        # # Test 19: Physical appearance
        # self.request("I have curly brown hair and green eyes. I'm about 5'8\" tall.")
        # self.validate("curly", "Hair description should be stored")
        # self.validate("green", "Eye color should be stored")

        # # Test 20: Favorite season
        # self.request("I love autumn because of the beautiful foliage and cool weather.")
        # self.validate("autumn", "Favorite season should be stored")

        # # Test 21: Childhood dream job
        # self.request("When I was a kid, I wanted to be an astronaut and explore space.")
        # self.validate("astronaut", "Childhood dream job should be stored")

        # # Test 22: Current project
        # self.request("I'm currently working on developing a mobile app for mental health awareness.")
        # self.validate("app", "Current project keyword should be stored")

        # # Test 23: Favorite sport
        # self.request("My favorite sport to watch is basketball, especially NBA games.")
        # self.validate("nba", "Favorite league should be stored")

        # # Test 24: Volunteer work
        # self.request("I volunteer at a local animal shelter every other weekend.")
        # self.validate("volunteer", "Volunteer activity should be stored")
        # self.validate("shelter", "Volunteer location should be stored")

        # # Test 25: Favorite cuisine
        # self.request("I absolutely love Italian cuisine, especially homemade pasta dishes.")
        # self.validate("pasta", "Favorite dish should be stored")

        # # Test 26: Biggest fear
        # self.request("My biggest fear is public speaking, but I'm working on overcoming it.")
        # self.validate("speaking", "Fear should be stored")

        # # Test 27: Favorite holiday
        # self.request("Christmas is my favorite holiday. I love the festive atmosphere and family gatherings.")
        # self.validate("christmas", "Favorite holiday should be stored")

        # # Test 28: Childhood pet
        # self.request("I had a pet hamster named Whiskers when I was 10 years old.")
        # self.validate("hamster", "Childhood pet should be stored")
        # self.validate("whiskers", "Pet name should be stored")

        # # Test 29: Dream vacation
        # self.request("My dream vacation is to visit the Galapagos Islands and see the unique wildlife.")
        # self.validate("galapagos", "Dream vacation destination should be stored")

        # # Test 30: Personal goal
        # self.request("One of my personal goals is to learn to speak fluent Mandarin Chinese within the next three years.")
        # self.validate("mandarin", "Language learning goal should be stored")

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