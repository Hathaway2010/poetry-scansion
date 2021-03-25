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
        self.assertEqual(__str__(u), "someone, Promoted: False")

class TestPronunciation(TestCase):
    @classmethod
    def setUpTestData(cls):
        Pronunciation.objects.create(word="moon", stress="")
