# Generated by Django 5.0.7 on 2024-07-13 11:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_category_options_alter_post_created_on'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='created_on',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
