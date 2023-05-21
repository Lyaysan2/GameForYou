# Generated by Django 4.1.5 on 2023-05-20 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_alter_systemcharacteristics_os'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='critics_score',
            field=models.FloatField(blank=True, null=True, verbose_name='Оценка критиков'),
        ),
        migrations.AddField(
            model_name='game',
            name='developer',
            field=models.CharField(blank=True, max_length=256, verbose_name='Разработчики'),
        ),
        migrations.AddField(
            model_name='game',
            name='directx',
            field=models.CharField(blank=True, max_length=256, verbose_name='DirectX'),
        ),
        migrations.AddField(
            model_name='game',
            name='graphics',
            field=models.CharField(blank=True, max_length=256, verbose_name='Видеокарта'),
        ),
        migrations.AddField(
            model_name='game',
            name='os',
            field=models.CharField(blank=True, max_length=256, verbose_name='Операционная система'),
        ),
        migrations.AddField(
            model_name='game',
            name='popularity',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество отзывов'),
        ),
        migrations.AddField(
            model_name='game',
            name='price',
            field=models.IntegerField(blank=True, null=True, verbose_name='Стоимость игры'),
        ),
        migrations.AddField(
            model_name='game',
            name='processor',
            field=models.CharField(blank=True, max_length=256, verbose_name='Процессор'),
        ),
        migrations.AddField(
            model_name='game',
            name='ram',
            field=models.IntegerField(blank=True, null=True, verbose_name='Оперативная память'),
        ),
        migrations.AddField(
            model_name='game',
            name='release_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата релиза'),
        ),
        migrations.AddField(
            model_name='game',
            name='reviews',
            field=models.CharField(blank=True, max_length=256, verbose_name='Оценка пользователей'),
        ),
        migrations.AddField(
            model_name='game',
            name='storage',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество свободного места'),
        ),
        migrations.AddField(
            model_name='game',
            name='tags',
            field=models.CharField(blank=True, max_length=400, verbose_name='Жанры'),
        ),
        migrations.AlterField(
            model_name='systemcharacteristics',
            name='directx',
            field=models.CharField(blank=True, choices=[('12.0', '12.0'), ('11.0', '11.0'), ('10.0', '10.0'), ('9.0', '9.0'), ('9.0c', '9.0c'), ('9.0b', '9.0b'), ('9.0a', '9.0a'), ('8.1', '8.1'), ('8.0', '8.0'), ('7.1', '7.1'), ('7.0', '7.0'), ('7.0a', '7.0a'), ('6.0', '6.0'), ('5.2', '5.2')], max_length=256, verbose_name='DirectX'),
        ),
        migrations.AlterField(
            model_name='systemcharacteristics',
            name='os',
            field=models.CharField(blank=True, choices=[('Windows 11', 'Windows 11'), ('Windows 10', 'Windows 10'), ('Windows 8.1', 'Windows 8.1'), ('Windows 8.0', 'Windows 8.0'), ('Windows 7', 'Windows 7'), ('Windows Vista', 'Windows Vista'), ('Windows XP', 'Windows XP')], max_length=256, verbose_name='Операционная система'),
        ),
    ]