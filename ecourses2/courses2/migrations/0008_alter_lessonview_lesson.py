# Generated by Django 4.0.2 on 2022-03-13 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses2', '0007_lessonview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonview',
            name='lesson',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='courses2.lesson'),
        ),
    ]
