from django.test import TestCase
from django.test import Client
from django.urls import reverse
from app.views import index, about, import_poem, poem, choose_poem, automated, own_poem
from app.models import User, Pronunciation, Poem, Algorithm, PoemScansion

client = Client()

class TestIndexGet(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
        User.objects.create_user("someone", password="12345", points=10, promoted=True)
        User.objects.create_user("squirrel", password="password", points=9, promoted=False)

    def test_get_index_not_authenticated(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/index.html")
        self.assertEqual(response.context[0]["poem"].title, "A Sea Dirge")

    def test_get_index_not_promoted(self):
        self.client.login(username="squirrel", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/index.html")
        self.assertEqual(response.context[0]["poem"].title, "A Sea Dirge")

    def test_get_index_promoted(self):
        self.client.login(username="someone", password="12345")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/index.html")
        self.assertEqual(response.context[0]["poem"].title, "")

class TestIndexPut(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel", scansion="/ /u ", human_scanned=True)
        Poem.objects.create(poem="squirrel moon", scansion="?? ? ")
        User.objects.create_user("someone", password="12345", points=10, promoted=True)
        User.objects.create_user("squirrel", password="password", points=9, promoted=False)
    # Do I really need to test not_authenticated, since the JavaScript does not send put requests for users who aren't?
    def test_put_index_not_authenticated(self):
        response= self.client.put(reverse("index"), '{"scansion": "u u/ ", "id": 1}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poem.objects.all()[0].scansion, "/ /u ")

    def test_put_index_not_promoted(self):
        self.client.login(username="squirrel", password="password")
        response = self.client.put(reverse("index"), '{"score": 1}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poem.objects.get(pk=1).scansion, "/ /u ")
        self.assertEqual(Poem.objects.get(pk=2).scansion, "?? ? ")
        sq = User.objects.get(username="squirrel")
        self.assertEqual(sq.points, 10)
        self.assertTrue(sq.promoted)

    def test_put_index_promoted_human_scanned(self):
        self.client.login(username="someone", password="12345")
        response = self.client.put(reverse("index"), '{"scansion": "/ uu ", "id": 1}')
        self.assertEqual(response.status_code, 200)
        s = User.objects.get(username="someone")
        self.assertEqual(s.points, 10)
        self.assertTrue(s.promoted)
        moonsquirrel = Poem.objects.get(pk=1)
        self.assertEqual(moonsquirrel.scansion, "/ uu ")
        self.assertTrue(moonsquirrel.human_scanned)

    def test_put_index_promoted_computer_scanned(self):
        self.client.login(username="someone", password="12345")
        response = self.client.put(reverse("index"), '{"scansion": "/u / ", "id": 2}')
        self.assertEqual(response.status_code, 200)
        squirrelmoon = Poem.objects.get(pk=2)
        self.assertEqual(squirrelmoon.scansion, "/u / ")
        self.assertTrue(squirrelmoon.human_scanned)

class TestAbout(TestCase):
    def test_about(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/about.html")

class TestImportPoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser("someone", password="12345", points=10, promoted=True)
        User.objects.create_user("squirrel", password="password", points=9, promoted=False)
        Algorithm.objects.create(name="House Robber Scan",
                                 about="words",
                                 function_name="house_robber_scan",
                                 preferred=True)

    def test_get_import_poem_not_authenticated(self):
        response = self.client.get(reverse("import_poem"))
        self.assertEqual(response.status_code, 302)

    def test_get_import_poem_not_admin(self):
        self.client.login(username="squirrel", password="password")
        response = self.client.get(reverse("import_poem"))
        self.assertEqual(response.status_code, 302)

    def test_get_import_poem_admin(self):
        self.client.login(username="someone", password="12345")
        response = self.client.get(reverse("import_poem"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/import_poem.html")

    def test_post_import_poem_not_authenticated(self):
        response = self.client.post(reverse("import_poem"),
                                    {"title": "Moon Squirrel",
                                     "poem": "The squirrel\nis in the moon",
                                     "poet": "Moon Squirrel"})
        self.assertEqual(response.status_code, 302)

    def test_post_import_poem_admin(self):
        self.client.login(username="someone", password="12345")
        response = self.client.post(reverse("import_poem"),
                                    {"title": "Moon Squirrel",
                                     "poem": "The squirrel\nis in the moon",
                                     "poet": "Moon Squirrel"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"/ u/ \nu / u / ")
        self.assertEqual(Poem.objects.all().count(), 1)
        self.assertEqual(Poem.objects.all()[0].title, "Moon Squirrel")

class TestPoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
        Poem.objects.create(poem="squirrel moon", human_scanned=True)
        Poem.objects.create(poem="The moon is a wavering rim where one fish slips.")

    def test_poem(self):
        response = self.client.get(reverse("poem", kwargs={"id": 2}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/index.html")
        self.assertEqual(response.context[0]["poem"].poem, "squirrel moon")


class TestChoosePoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
        Poem.objects.create(poem="squirrel moon", human_scanned=True)
        Poem.objects.create(poem="The moon is a wavering rim where one fish slips.")

    def test_choose_poem(self):
        response = self.client.get(reverse("choose_poem"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/choose_poem.html")
        self.assertQuerysetEqual(response.context[0]["human_list"],
                                 Poem.objects.filter(poem="squirrel moon"),
                                 transform=lambda x: x)
        self.assertQuerysetEqual(response.context[0]["computer_list"],
                                 Poem.objects.filter(human_scanned=False),
                                 transform=lambda x: x)

class TestAutomated(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
        Poem.objects.create(poem="squirrel moon")
        Poem.objects.create(poem="The moon is a wavering rim where one fish slips.")
        Algorithm.objects.create(name="Original Scan",
                                 about="words",
                                 function_name="original_scan")
        Algorithm.objects.create(name="House Robber Scan",
                                 about="words",
                                 function_name="house_robber_scan",
                                 preferred=True)

    def test_automated_no_id(self):
        line = "The moon is a wavering rim where one fish slips."
        house_robber_scansions = {"moon squirrel": "/ u/ ",
                                  "squirrel moon": "/u / ",
                                  line: "u / u / u/u / u / u / "}
        response = self.client.get(reverse("automated"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/automated.html")
        self.assertIn(response.context[0]["poem"], Poem.objects.all())
        self.assertQuerysetEqual(response.context[0]["algorithms"],
                         Algorithm.objects.all().order_by("-preferred"),
                         transform=lambda x: x)
        self.assertEqual(response.context[0]["scansions"][0].type.function_name,
                         "house_robber_scan")
        self.assertEqual(response.context[0]["scansions"][0].scansion,
                         house_robber_scansions[response.context[0]["poem"].poem])

    def test_automated_id(self):
        for poem in Poem.objects.all():
            print(poem.poem, poem.pk)
        response = self.client.get(reverse("automated", kwargs={"id": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/automated.html")
        self.assertEqual(response.context[0]["poem"].poem, "moon squirrel")
        self.assertQuerysetEqual(response.context[0]["algorithms"],
                         Algorithm.objects.all().order_by("-preferred"),
                         transform=lambda x: x)
        self.assertEqual(response.context[0]["scansions"][0].type.function_name,
                         "house_robber_scan")
        self.assertEqual(response.context[0]["scansions"][0].scansion,
                         "/ u/ ")

class TestOwnPoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        Algorithm.objects.create(name="Original Scan",
                                 about="words",
                                 function_name="original_scan")
        Algorithm.objects.create(name="House Robber Scan",
                                 about="words",
                                 function_name="house_robber_scan",
                                 preferred=True)

    def test_own_poem_get(self):
        response = self.client.get(reverse("own_poem"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/own_poem.html")

    def test_own_poem_post(self):
        response = self.client.post(reverse("own_poem"),
                                    {"title": "",
                                     "poem": "moon squirrel",
                                     "poet": "Moon Squirrel"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "app/automated.html")
        self.assertEqual(response.context[0]["poem"].poem, "moon squirrel")
        self.assertEqual(response.context[0]["scansions"][0].scansion,
                         "/ u/ ")
        self.assertEqual(response.context[0]["scansions"][1].scansion,
                         "? ?? ")
        self.assertEqual(response.context[0]["algorithms"][0].function_name,
                         "house_robber_scan")
