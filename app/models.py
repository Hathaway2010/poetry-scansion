from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    points = models.IntegerField(default=0)
    promoted = models.BooleanField(default=False)

class Pronunciation(models.Model):
    word = models.CharField(max_length=50, db_index=True)
    stresses = models.CharField(max_length=20, blank=True)
    popularity = models.IntegerField(default=0)

class Poem(models.Model):
    title = models.TextField()
    poem = models.TextField()
    scansion = models.TextField()
    human_scanned = models.BooleanField(default=False)
    poet = models.TextField()

class Algorithm(models.Model):
    name = models.TextField()
    about = models.TextField()
    function_name = models.TextField()
    preferred = models.BooleanField(default=False)

class PoemScansion(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    scansion = models.TextField()
    type = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
