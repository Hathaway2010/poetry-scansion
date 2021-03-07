from django.contrib import admin
from .models import User, Pronunciation, Poem

# Register your models here.
admin.site.register(User)
admin.site.register(Pronunciation)
admin.site.register(Poem)
