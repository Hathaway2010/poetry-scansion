from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.contrib.auth import (SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY, get_user_model)
from django.contrib.sessions.backends.db import SessionStore
from django.test import tag

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def create_session_cookie(user):
    session = SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()
    cookie = {
        'name': settings.SESSION_COOKIE_NAME,
        'value': session.session_key,
        'secure': False,
        'path': '/',
    }

    return cookie

@tag("selenium")
class TestIndex(StaticLiveServerTestCase):
    port=8000

    def setUp(self):
        super(TestIndex, self).setUp()
        Poem.objects.create(poem="moon squirrel", scansion="/ u/ ")
        User.objects.create_user(username="squirrel", password="asdf", points=9, promoted=False)
        User.objects.create_user(username="admin", password="admin123", points=10, promoted=True)
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'browser':'ALL' }
        options = Options()
        # https://stackoverflow.com/questions/48450594/selenium-timed-out-receiving-message-from-renderer
        options.add_argument("start-maximized"); # https://stackoverflow.com/a/26283818/1689770
        options.add_argument("enable-auomation"); # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--headless"); # only if you are ACTUALLY running headless
        options.add_argument("--no-sandbox"); # https://stackoverflow.com/a/50725918/1689770
        # options.add_argument("--disable-infobars"); # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--disable-dev-shm-usage"); # https://stackoverflow.com/a/50725918/1689770
        # options.add_argument("--disable-browser-side-navigation"); # https://stackoverflow.com/a/49123152/1689770
        options.add_argument("--disable-gpu"); # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
        options.add_argument("window-size=1280x600")
        self.selenium = webdriver.Chrome(chrome_options=options, desired_capabilities=d)
        self.selenium.implicitly_wait(20)

    def tearDown(self):
        self.selenium.quit()
        super(TestIndex, self).tearDown()

    def test_setup(self):
        p = Poem.objects.all()
        self.assertEqual(p.count(), 1)
        self.assertEqual(p[0].poem, "moon squirrel")
        u = User.objects.all()
        self.assertEqual(u.count(), 2)
        self.assertEqual(u[0].username, "squirrel")
        self.assertEqual(u[1].username, "admin")

    def test_layout_not_promoted(self):
        session_cookie = create_session_cookie(User.objects.get(username="squirrel"))
        self.selenium.get(f"{self.live_server_url}")
        self.selenium.add_cookie(session_cookie)
        self.selenium.refresh()
        self.selenium.get(f"{self.live_server_url}")
        links = self.selenium.find_elements_by_tag_name("a")
        self.assertEqual(len(links), 6)
        score = self.selenium.find_elements_by_id("score")
        self.assertEqual(len(score), 1)
        self.assertEqual(score[0].text, "9")

    def test_layout_promoted(self):
        session_cookie = create_session_cookie(User.objects.get(username="admin"))
        self.selenium.get(f"{self.live_server_url}")
        self.selenium.add_cookie(session_cookie)
        self.selenium.refresh()
        self.selenium.get(f"{self.live_server_url}")
        links = self.selenium.find_elements_by_tag_name("a")
        self.assertEqual(len(links), 6)
        score = self.selenium.find_elements_by_id("score")
        self.assertEqual(len(score), 0)

    def test_interface_not_promoted(self):
        session_cookie = create_session_cookie(User.objects.get(username="squirrel"))
        self.selenium.get(f"{self.live_server_url}")
        self.selenium.add_cookie(session_cookie)
        self.selenium.refresh()
        self.selenium.get(f"{self.live_server_url}")
        lines = self.selenium.find_elements_by_tag_name("table")
        self.assertEqual(len(lines), 9)

    def test_interface_promoted(self):
        session_cookie = create_session_cookie(User.objects.get(username="admin"))
        self.selenium.get(f"{self.live_server_url}")
        self.selenium.add_cookie(session_cookie)
        self.selenium.refresh()
        self.selenium.get(f"{self.live_server_url}")
        lines = self.selenium.find_elements_by_tag_name("table")
        self.assertEqual(len(lines), 1)
        self.assertEqual(self.selenium.find_element_by_id("poem-text").text, "moon squirrel")

    @tag("slow")
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

    @tag("slow")
    def test_login(self):
        self.selenium.get(f"{self.live_server_url}/login")
        self.selenium.find_element_by_id("username").send_keys("squirrel")
        self.selenium.find_element_by_id("password").send_keys("asdf")
        self.selenium.find_element_by_id("submit").click()
        links = self.selenium.find_elements_by_tag_name("a")
        self.assertEqual(len(links), 6)
        score = self.selenium.find_elements_by_id("score")
        self.assertEqual(len(score), 1)
        self.assertEqual(score[0].text, "9")
