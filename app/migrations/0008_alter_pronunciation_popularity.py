# Generated by Django 3.2 on 2021-04-24 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20210325_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pronunciation',
            name='popularity',
            field=models.IntegerField(default=0),
        ),
    ]
