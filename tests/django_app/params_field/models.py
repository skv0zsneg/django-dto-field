from django.db import models

from django_dict_field import DictField


class ModelForTest(models.Model):
    default_dict_field = DictField()
