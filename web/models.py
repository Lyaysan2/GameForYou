from django.db import models
from django.contrib.auth import get_user_model
from utils.mychoice import *

User = get_user_model()


class SystemCharacteristics(models.Model):
    os = models.CharField(max_length=256, blank=True, choices=OS_CHOICES, verbose_name='Операционная система')
    processor = models.CharField(max_length=256, blank=True, choices=PROCESSOR_CHOICES, verbose_name='Процессор')
    memory = models.IntegerField(blank=True, null=True, verbose_name='Оперативная память')
    graphics = models.CharField(max_length=256, blank=True, choices=GRAPHICS_CHOICES, verbose_name='Видеокарта')
    directx = models.CharField(max_length=256, blank=True, choices=DIRECTX_CHOICES, verbose_name='DirectX')
    storage = models.IntegerField(blank=True, null=True, verbose_name='Свободное место на диске')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')


class Game(models.Model):
    name = models.CharField(max_length=256, blank=True, verbose_name='Название игры')
    link = models.CharField(max_length=256, blank=True, verbose_name='Ссылка на игру')
    users = models.ManyToManyField(User, verbose_name='Пользователь')
