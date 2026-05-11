# django-dto-field

[![PyPI version](https://img.shields.io/pypi/v/django-dto-field.svg)](https://pypi.org/project/django-dto-field/)
[![PyPI license](https://img.shields.io/pypi/l/django-dto-field.svg)](https://pypi.python.org/pypi/django-dto-field/)
[![Python Version](https://img.shields.io/pypi/pyversions/django-dto-field.svg)](https://pypi.org/project/django-dto-field/)

[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![test](https://github.com/skv0zsneg/django-dto-field/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dto-field/actions/workflows/test.yml)
[![typing & lint](https://github.com/skv0zsneg/django-dto-field/actions/workflows/typing_and_lint.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dto-field/actions/workflows/typing_and_lint.yml)

_Storing DTO data in easy-to-use and production-ready Django Model Field with fast [de]serialization._

A custom Django Model Field that can serialize and deserialize for different types of DTO (Data-Transfer-Object). `DTOField` detect DTO type and serialize the most efficiently. Also it has own binary container to maintain data integrity and economical storage. 


## ✨ Features

- [X] All DB support (if DB support BinaryFiled)
- [ ] Zip field for size saving (optional)
- [X] Supports pure [`dict`](#dict) as DTO
- [X] Supports [`dataclass`](#dataclass) as DTO
- [ ] Supports `pydantic` as DTO
- [ ] Supports `marshmallow` as DTO
- [ ] Supports `attrs` as DTO
- [ ] Supports `adapdtix` as DTO


## ⬇️ Install

```bash
$ pip install django-dto-field
```

## 🚀 Quick start

Choose your DTO: [`dict`](#dict), [`dataclass`](#dataclass)

### `dict`

We support pure `dict` for using it like DTO object. The main different between `dict` and other DTO types is that `dict` has no validation and `DTOField` uses it by default.

Also we have some [benchmarks](/tests/e2e/dict_field/management/commands/benchmark.py) with default `JSONField`. And they shows that `DTOField` is 2.4x faster on write operation (thanks to amazing [msgspec](https://github.com/jcrist/msgspec) lib). 

![JSONField vs DTOField write](/docs/media/JSONField%20и%20DTOField.png)

1. Set `DTOField` to your model:

```python
>>> from django.db.models import CharField
>>> from django_dto_field import DTOField

>>> class Country(Model):
...    name = CharField()
...    city = DTOField()
```

2. Use it:

```python
>>> city = {"name": "Capitol", "districts": [f"d{i}" for i in range(1, 14)]}
>>> created_country = Country.objects.create(name="Panem", city=city)

>>> from_db_country = Country.objects.get(pk=created_country.pk)
>>> assert isinstance(from_db_country.city, dict)
>>> assert from_db_country.city == city
```

### `dataclass`

We support `dataclass` object as DTO. You can use it simply without thinking of serialization, deserialization and validation. `DTOField` will do it for you.

1. Set `dataclass` schema:

```python
>>> from dataclasses import dataclass

>>> @dataclass
... class City:
...     name: str
...     districts: list[str]
```

2. Set `DTOField` to your model and add schema.

```python
>>> from django.db.models import CharField
>>> from django_dto_field import DTOField

>>> class Country(Model):
...    name = CharField()
...    city = DTOField(schema=City)
```

3. Use it:

```python
>>> city = City(name="Capitol", districts=[f"d{i}" for i in range(1, 14)])
>>> created_country = Country.objects.create(name="Panem", city=city)

>>> from_db_country = Country.objects.get(pk=created_country.pk)
>>> assert isinstance(from_db_country.city, City)
>>> assert from_db_country.city == city
```

Validation error will raise if wrong schema will appear ([what if schema change?](#what-if-schema-will-change)):

```python
>>> @dataclass
... class WrongCity:
...     addresses: list[str]
...

>>> wrong_city = WrongCity(addresses=[])
>>> from_db_country.city = wrong_city
Traceback (most recent call last):
    ...
ValidationError: given value 'WrongCity(addresses=[])' did not match schema 'City'
```


### What if schema will change?

The goal of `DTOField` is to give you an easy tool for working with different DTO's objects but not how to manipulate them. This is why we will never give migration features.

But it's not a problem! Often you can make migration with 3 steps:

1. Define the new `DTOField` with your new schema.
2. Write new custom Django migration to get, change and save updated data to new field.
3. Delete old field.  


## 🤗 Author

Made with love by [@skv0zsneg](https://github.com/skv0zsneg)
