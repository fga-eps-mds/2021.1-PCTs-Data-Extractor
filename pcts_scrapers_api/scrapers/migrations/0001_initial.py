# Generated by Django 3.2.8 on 2021-10-17 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Scraper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=100, unique=True, verbose_name='Site Name')),
                ('url_root', models.CharField(max_length=1024, unique=True, verbose_name='Root Url')),
                ('task_name_prefix', models.CharField(max_length=50, unique=True, verbose_name='Task Name Prefix')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScraperExecutionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=100, verbose_name='Task Name')),
                ('start_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Start Datetime')),
                ('end_datetime', models.DateTimeField(null=True, verbose_name='End Datetime')),
                ('status', models.IntegerField(choices=[(1, 'STARTED'), (2, 'SUCCESS'), (3, 'FAILED')], default=1, verbose_name='Execution Status')),
                ('scraper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapers.scraper')),
            ],
        ),
        migrations.CreateModel(
            name='ScraperExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.UUIDField(verbose_name='Task Run UUID')),
                ('task_name', models.CharField(max_length=100, verbose_name='Task Name')),
                ('start_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Start Datetime')),
                ('end_datetime', models.DateTimeField(null=True, verbose_name='End Datetime')),
                ('keyword', models.CharField(max_length=1024, verbose_name='Keyword')),
                ('status', models.IntegerField(choices=[(1, 'STARTED'), (2, 'SUCCESS'), (3, 'FAILED')], default=1, verbose_name='Execution Status')),
                ('scraped_pages', models.IntegerField()),
                ('saved_records', models.IntegerField()),
                ('droped_records', models.IntegerField()),
                ('scraper_execution_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapers.scraperexecutiongroup')),
            ],
        ),
    ]
