from django.test import TestCase
from app.models import User, Pronunciation, Poem, Algorithm, PoemScansion

class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="someone", points=0)

    def test_user(self):
        u = User.objects.filter(username="someone")
        self.assertTrue(u.exists())
        self.assertEqual(u[0].points, 0)
        self.assertFalse(u[0].promoted)
        self.assertEqual(u[0].__str__(), "someone, Promoted: False")

class TestPronunciation(TestCase):
    @classmethod
    def setUpTestData(cls):
        Pronunciation.objects.create(word="moon", stresses="/")

    def test_pronunciation(self):
        p = Pronunciation.objects.filter(word="moon")
        self.assertTrue(p.exists())
        self.assertEqual(p[0].stresses, "/")
        self.assertEqual(p[0].popularity, 0)
        self.assertEqual(p[0].__str__(), "moon, /, popularity: 0")

class TestPoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        poem = """THE moon is a wavering rim where one fish slips,
                The water makes a quietness of sound;
                Night is an anchoring of many ships
                Home-bound."""
        scansion = """u / u u /uu / u / u /
                   u /u / u /u/ u /
                   / u u /u/ u /u /
                   u/ """
        Poem.objects.create(title="Home-Bound", poem=poem, scansion=scansion,
                            human_scanned=True, poet="Auslander, Joseph")
        Poem.objects.create(poem="moon squirrel")

    def test_regular_poem(self):
        p = Poem.objects.filter(poet="Auslander, Joseph")
        self.assertTrue(p.exists())
        p2 = Poem.objects.filter(poem="moon squirrel")
        self.assertTrue(p2.exists())
        self.assertEqual(p2[0].title, "")
        self.assertFalse(p2[0].human_scanned)

class TestAlgorithm(TestCase):
    @classmethod
    def setUpTestData(cls):
        Algorithm.objects.create(name="Real Scan", about="gets up to 95% right",
                                 function_name="real_scan")
        Algorithm.objects.create(name="Imaginary Scan",
                                 about="This scan passes a scansion Turing test!",
                                 function_name="imaginary_scan", preferred=True)

    def test_algorithm(self):
        a = Algorithm.objects.all().order_by("-preferred")
        self.assertTrue(a.exists())
        self.assertEqual(a[0].name, "Imaginary Scan")
        self.assertEqual(a[1].name, "Real Scan")
        self.assertFalse(a[1].preferred)

class TestPoemScansion(TestCase):
    @classmethod
    def setUpTestData(cls):
        Algorithm.objects.create(name="Real Scan", about="gets up to 95% right",
                                 function_name="real_scan")
        Poem.objects.create(poem="moon squirrel")
        p = Poem.objects.get(poem="moon squirrel")
        a = Algorithm.objects.get(name="Real Scan")
        PoemScansion.objects.create(poem=p, scansion="/ u/ ", type=a)

    def test_poem_scansion(self):
        ps = PoemScansion.objects.all()
        self.assertTrue(ps.exists())
        self.assertEqual(ps[0].poem.poem, "moon squirrel")
        self.assertFalse(ps[0].poem.human_scanned)
        self.assertEqual(ps[0].scansion, "/ u/ ")
        self.assertEqual(ps[0].type.function_name, "real_scan")
