# Generated by Django 4.1.5 on 2023-05-12 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_alter_systemcharacteristics_directx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemcharacteristics',
            name='os',
            field=models.CharField(blank=True, max_length=256, verbose_name='Операционная система'),
        ),
    ]