from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from app.views import index, about, import_poem, poem, choose_poem, automated, own_poem
from app.models import User, Pronunciation, Poem, Algorithm, PoemScansion

TEMPEST_STRESSED = ["scansion0-1", "scansion0-2", "scansion0-4", "scansion0-5",
                    "scansion1-0", "scansion1-2", "scansion1-4", "scansion1-5",
                    "scansion2-0", "scansion2-2", "scansion2-4", "scansion2-6",
                    "scansion3-0", "scansion3-1", "scansion3-3", "scansion3-5",
                    "scansion4-2", "scansion4-4",
                    "scansion5-0", "scansion5-1", "scansion5-2", "scansion5-4",
                    "scansion6-0", "scansion6-1", "scansion6-2", "scansion6-4",
                    "scansion7-0", "scansion7-3",
                    "scansion8-0", "scansion8-2"]

@tag("selenium")
class TestIndex(StaticLiveServerTestCase):
    port=8000
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'browser':'ALL' }
        options = Options()
        # https://stackoverflow.com/questions/48450594/selenium-timed-out-receiving-message-from-renderer
        options.add_argument("start-maximized") # https://stackoverflow.com/a/26283818/1689770
        options.add_argument("enable-automation") # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--headless") # only if you are ACTUALLY running headless
        options.add_argument("--no-sandbox") # https://stackoverflow.com/a/50725918/1689770
        options.add_argument("--disable-dev-shm-usage") # https://stackoverflow.com/a/50725918/1689770
        options.add_argument("--disable-gpu") # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
        options.add_argument("window-size=1280x600")
        cls.selenium = webdriver.Chrome(chrome_options=options, desired_capabilities=d)
        cls.selenium.implicitly_wait(20)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_layout(self):
        self.selenium.get(f"{self.live_server_url}")
        site = self.selenium.find_elements_by_tag_name("body")
        self.assertEqual(len(site), 1)
        links = self.selenium.find_elements_by_tag_name("a")
        self.assertEqual(len(links), 7)

    def test_render_interface(self):
        self.selenium.get(f"{self.live_server_url}")
        lines = self.selenium.find_elements_by_tag_name("table")
        self.assertEqual(len(lines), 9)
        first_word = self.selenium.find_element_by_id("word0-0")
        self.assertEqual(first_word.text, "Full")
        first_scansion = self.selenium.find_element_by_id("scansion0-0")
        self.assertEqual(first_scansion.text, "u")
        seachange = self.selenium.find_element_by_id("word4-4")
        self.assertEqual(seachange.text, "sea-change")


    def test_change_unstressed_to_stressed(self):
        self.selenium.get(f"{self.live_server_url}")
        first_scansion = self.selenium.find_element_by_id("scansion0-0")
        self.assertEqual(first_scansion.text, "u")
        sym = first_scansion.find_element_by_class_name("symbol")
        sym.click()
        self.assertEqual(first_scansion.text, "/")

    def test_add_syllable(self):
        self.selenium.get(f"{self.live_server_url}")
        first_scansion = self.selenium.find_element_by_id("scansion0-0")
        self.assertEqual(first_scansion.text, "u")
        first_pmc = self.selenium.find_element_by_id("pm0-0")
        plus = first_pmc.find_element_by_class_name("plus")
        plus.click()
        self.assertEqual(first_scansion.text, "uu")

    def test_remove_syllables(self):
        self.selenium.get(f"{self.live_server_url}")
        seachange = self.selenium.find_element_by_id("scansion4-4")
        self.assertEqual(seachange.text, "uu")
        sc_pmc = self.selenium.find_element_by_id("pm4-4")
        minus = sc_pmc.find_element_by_class_name("minus")
        minus.click()
        self.assertEqual(seachange.text, "u")
        minus.click()
        self.assertEqual(seachange.text, "")
        minus.click()
        self.assertEqual(seachange.text, "")


    def test_submit_unchanged_scansion_not_authenticated(self):
        self.selenium.get(f"{self.live_server_url}")
        submit = self.selenium.find_element_by_id("submit-scansion")
        submit.click()
        # to debug: for entry in self.selenium.get_log("browser"):
        #      print(entry)
        alert = self.selenium.switch_to_alert()
        alert_text = alert.text
        alert.accept()
        self.assertEqual(alert_text, "If you were logged in, you would have lost a point! Look at the poem to see where your scansion differed (63% of words) from the most recent authoritative scansion.")
        words = self.selenium.find_elements_by_class_name("word")
        scansions = self.selenium.find_elements_by_class_name("scansion")
        for pair in zip(words, scansions):
            if pair[1].get_attribute("id") in TEMPEST_STRESSED:
                self.assertEqual(pair[0].value_of_css_property("background-color"),
                                 "rgba(255, 204, 204, 1)")
                self.assertEqual(pair[1].value_of_css_property("background-color"),
                                 "rgba(255, 204, 204, 1)")
            else:
                self.assertEqual(pair[0].value_of_css_property("background-color"),
                                 "rgba(153, 255, 187, 1)")
                self.assertEqual(pair[1].value_of_css_property("background-color"),
                                 "rgba(153, 255, 187, 1)")
        self.assertFalse(submit.is_enabled())

    def test_submit_terrible_scansion_not_authenticated(self):
        self.selenium.get(f"{self.live_server_url}")
        self.selenium.refresh()
        minuses = self.selenium.find_elements_by_class_name("minus")
        for minus in minuses:
            minus.click()
        submit = self.selenium.find_element_by_id("submit-scansion")
        submit.click()
        alert = self.selenium.switch_to_alert()
        alert_text = alert.text
        alert.accept()
        self.assertEqual(alert_text, "If you were logged in, you would have lost a point! Look at the poem to see where your scansion differed (100% of words) from the most recent authoritative scansion.")
        words = self.selenium.find_elements_by_class_name("word")
        for word in words:
            self.assertEqual(word.value_of_css_property("background-color"), "rgba(255, 204, 204, 1)")
        self.assertFalse(submit.is_enabled())

    def test_submit_correct_scansion_not_authenticated(self):
        self.selenium.get(f"{self.live_server_url}")
        for word in TEMPEST_STRESSED:
            cell = self.selenium.find_element_by_id(word)
            syms = cell.find_elements_by_class_name("symbol")
            # through a weird stroke of luck *every single multi-syllable word*
            # in this poem is accented on its first syllable!
            syms[0].click()
        submit = self.selenium.find_element_by_id("submit-scansion")
        submit.click()
        alert = self.selenium.switch_to.alert
        alert_text = alert.text
        alert.accept()
        self.assertEqual(alert_text, "If you were logged in, you would have gained a point! Look at the poem to see where your scansion differed (0% of words) from the most recent authoritative scansion.")
        words = self.selenium.find_elements_by_class_name("word")
        for word in words:
            self.assertEqual(word.value_of_css_property("background-color"), "rgba(153, 255, 187, 1)")
        self.assertFalse(submit.is_enabled())

    def test_submit_middling_scansion_not_authenticated(self):
        self.selenium.get(f"{self.live_server_url}")
        for word in TEMPEST_STRESSED[: 18]:
            cell = self.selenium.find_element_by_id(word)
            syms = cell.find_elements_by_class_name("symbol")
            syms[0].click()
        submit = self.selenium.find_element_by_id("submit-scansion")
        submit.click()
        alert = self.selenium.switch_to.alert
        alert_text = alert.text
        alert.accept()
        self.assertEqual(alert_text, "If you were logged in, you would have neither gained nor lost a point. Look at the poem to see where your scansion differed (25% of words) from the most recent authoritative scansion.")
        words = self.selenium.find_elements_by_class_name("word")
        scansions = self.selenium.find_elements_by_class_name("scansion")
        for pair in zip(words, scansions):
            pair_id = pair[1].get_attribute("id")
            if pair_id in TEMPEST_STRESSED[18: ]:
                self.assertEqual(pair[0].value_of_css_property("background-color"),
                                 "rgba(255, 204, 204, 1)")
                self.assertEqual(pair[1].value_of_css_property("background-color"),
                                 "rgba(255, 204, 204, 1)")
            else:
                self.assertEqual(pair[0].value_of_css_property("background-color"),
                                 "rgba(153, 255, 187, 1)")
                self.assertEqual(pair[1].value_of_css_property("background-color"),
                                 "rgba(153, 255, 187, 1)")
