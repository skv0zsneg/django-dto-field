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

## ✅ Validate with Schemas

For validation `DictField` values you can use schema feature.

Just define schema with dataclasses or TypedDict (in future versions more scheme description will be added - check issues if you want to help):
```python
from dataclasses import dataclass

@dataclass
class Coords:
    latitude: float
    longitude: float

@dataclass
class City:
    name: str
    coords: Coords | None = None
    districts: list[str] = []
```

Then set it to `DictField` to `scheme` arg:
```python
class Country(Model):
    capital = DictField(schema=City)
```

And use it!
```python
# creating throw schema
my_capital = City(
    coords=Coords(latitude=123.456, longitude=456.123),
    name="Laplandia",
    districts=["first", "second"],
)

# ... or throw raw dict
my_capital = {
    "coords": {"latitude": 123.456, "longitude": 456.123},
    "name": "Laplandia",
    "districts": ["first", "second"],
}

my_country = Country.objects.create(capital=my_capital)

# use like schema vars or like raw dict
assert my_country.capital.coords.longitude == my_country.capital["coords"]["longitude"]

# validate values when changing
try:
    my_country.capital.coords = 42
except InvalidSchemaAttribute:
    # Handle invalid schema attribute cases
    pass
```

### Unexpected data

In perfect world when using schema you must be 100% sure that all DB's data is correspond to used schema. But field in storage can be changed directly bypass Django. Helpfully In this cases `DictFiled` will not raise exception on not valid data. Validation on reading from DB will work only if flag `strict_schema_validation` flag is set to `True`.

```python
class Country(Model):
    capital = DictField(schema=City, strict_schema_validation=True)

my_country = Country.objects.get(pk=123)
try:
    my_country.capital
except InvalidSchema:
    # Handle invalid schema cases
    pass
```


## 🤗 Author

Made with love by [@skv0zsneg](https://github.com/skv0zsneg)
