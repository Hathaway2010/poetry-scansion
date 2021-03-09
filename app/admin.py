from django.contrib import admin
from .models import User, Pronunciation, Poem, Algorithm, PoemScansion

# Register your models here.
admin.site.register(User)
admin.site.register(Pronunciation)
admin.site.register(Poem)
admin.site.register(Algorithm)
admin.site.register(PoemScansion)
