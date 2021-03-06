# Generated by Django 3.1.5 on 2021-03-09 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_remove_poem_likes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Algorithm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('about', models.TextField()),
                ('function_name', models.TextField()),
                ('preferred', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PoemScansion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scansion', models.TextField()),
                ('poem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.poem')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.algorithm')),
            ],
        ),
    ]
