# Generated by Django 2.0.3 on 2018-04-11 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='config_detail',
            field=models.TextField(default='null'),
        ),
    ]