# Generated by Django 3.2.8 on 2021-10-28 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawler',
            name='contains_dynamic_js_load',
            field=models.BooleanField(default=True, verbose_name='Contains Dynamic JS Loading'),
        ),
    ]