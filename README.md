# django-dict-field

[![PyPI version](https://img.shields.io/pypi/v/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)
[![Python Version](https://img.shields.io/pypi/pyversions/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)
[![PyPI license](https://img.shields.io/pypi/l/django-dict-field.svg)](https://pypi.python.org/pypi/django-dict-field/)
[![test](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml)
[![typing & lint](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml)

> ⚠️ This project under active developing.

Django extension for storing dict data in relation database field with fast performance and flex schema.

## 📍 Purpose

Sometimes we need to store some key value data in storages. Often it also need to be efficient for work with big data and have some validation and another features.

`django-dict-field` is a tool build around amazing [msgspec](https://github.com/jcrist/msgspec) serialization and validation library for solving this problems like a charm ✨

**DictField vs JSONField Benchmark**

Operations on 100 000 size dict on PostgreSQL DB. Script [here](/benchmarks/jsonfield_benchmark.py).

![DictField vs JSONField Benchmark](docs/media/bechmark.png)


## 🚀 Quick start

1. Install `django-dict-field`.

```
pip install django-dict-field
```

2. Add `DictField` to your model.

```python
from django.db.models import Model, CharField, DateTimeField
from django_dict_field import DictField

class Car(Model):
    model = CharField()
    creation_data = DateTimeField()
    configuration = DictField()  # for storing a lot of configuration settings
```

3. Work with it!

```python
# create
car = Car.objects.create(
    model="Toyota Camry",
    creation_data=datetime(2021, 3, 15),
    configuration={
        "capacity": 2.5,
        "drive": "FWD",
        "consumption": 6.8,
    }
)

# read
assert car.configuration["drive"] == "FWD"

# update
car.configuration["capacity"] = 2.8

# delete
del car.configuration["doors"]
```

## 🤗 Author

Made with love by [@skv0zsneg](https://github.com/skv0zsneg)
