from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import Client

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.views import index, about, import_poem, poem, choose_poem, automated, own_poem
from app.models import User, Pronunciation, Poem, Algorithm, PoemScansion

class TestIndex(StaticLiveServerTestCase):
    port=8000
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel", scansion="/ u/ ")
        User.objects.create_user(username="squirrel", password="asdf", points=9, promoted=False)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'browser':'ALL' }
        options = Options()
        # https://stackoverflow.com/questions/48450594/selenium-timed-out-receiving-message-from-renderer
        options.add_argument("start-maximized"); # https://stackoverflow.com/a/26283818/1689770
        options.add_argument("enable-automation"); # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--headless"); # only if you are ACTUALLY running headless
        options.add_argument("--no-sandbox"); # https://stackoverflow.com/a/50725918/1689770
        # options.add_argument("--disable-infobars"); # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--disable-dev-shm-usage"); # https://stackoverflow.com/a/50725918/1689770
        # options.add_argument("--disable-browser-side-navigation"); # https://stackoverflow.com/a/49123152/1689770
        options.add_argument("--disable-gpu"); # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
        options.add_argument("window-size=1280x600")
        cls.selenium = webdriver.Chrome(chrome_options=options, desired_capabilities=d)
        cls.selenium.implicitly_wait(20)
        client = Client()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_register(self):
        self.selenium.get(f"{self.live_server_url}/register")
        self.selenium.find_element_by_id("username").send_keys("supersquirrel")
        self.selenium.find_element_by_id("email").send_keys("squirrelly@squirrels.squirrels")
        self.selenium.find_element_by_id("password").send_keys("aaaaaa")
        self.selenium.find_element_by_id("confirmation").send_keys("aaaaaa")
        self.selenium.find_element_by_id("submit").click()
        self.assertEqual(User.objects.filter(username="supersquirrel")[0].email, "squirrelly@squirrels.squirrels")
        self.assertEqual(self.selenium.find_element_by_id("score").text, "0")
        self.selenium.find_element_by_id("logout").click()
        self.assertEqual(len(self.selenium.find_elements_by_id("score")), 0)
        self.selenium.find_element_by_id("login_link").click()
        self.selenium.find_element_by_id("username").send_keys("supersquirrel")
        self.selenium.find_element_by_id("password").send_keys("aaaaaa")
        self.selenium.find_element_by_id("submit").click()
        self.assertEqual(self.selenium.find_element_by_id("score").text, "0")
