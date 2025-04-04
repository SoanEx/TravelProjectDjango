# Generated by Django 5.1.6 on 2025-03-21 01:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='memberrelation',
            name='created_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='memberrelation',
            name='no_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookkeeping.record'),
        ),
        migrations.AlterField(
            model_name='record',
            name='note',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
