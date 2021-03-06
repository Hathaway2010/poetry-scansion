# Generated by Django 3.1.5 on 2021-02-15 22:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('poem', models.TextField()),
                ('scansion', models.TextField()),
                ('human_scanned', models.BooleanField(default=False)),
                ('poet', models.TextField()),
                ('likes', models.ManyToManyField(blank=True, related_name='primary_key', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
