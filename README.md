# django-dto-field

[![PyPI version](https://img.shields.io/pypi/v/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)
[![Python Version](https://img.shields.io/pypi/pyversions/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)
[![PyPI license](https://img.shields.io/pypi/l/django-dict-field.svg)](https://pypi.python.org/pypi/django-dict-field/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![test](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml)
[![typing & lint](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml)

Storing DTO data in Django model field with fast [de]serialization.

## ✨ Features

- [ ] Faster than [JSONField](#-benchmarks) wrappers
- [X] All DB support (if DB support BinaryFiled)
- [ ] Zip field for size saving (optional)
- [X] Supports pure `dict` as DTO
- [ ] Supports `TypedDict` as DTO
- [ ] Supports `dataclass` as DTO
- [ ] Supports `pydantic` as DTO
- [ ] Supports `marshmallow` as DTO
- [ ] Supports `attrs` as DTO
- [ ] Supports `adapdtix` as DTO


## ⬇️ Install

```bash
$ pip install django-dto-field
```

## 🚀 Quick start

Set dto field to your model

```python
>>> from django.db.models import CharField
>>> from django_dto_field import DtoField

>>> class Country(Model):
...    name = CharField()
...    city = DtoField()
```

And than use it as usual

```python
>>> from dataclasses import dataclass

>>> @dataclass  # <- Change to your favorite DTO
... class City:
...    name: str 
...    districts: list[str]

>>> city = City(name="Capitol", districts=[f"d{i}" for i in range(1, 14)])
>>> country = Country.objects.create(name="Panem", city=city)

>>> assert isinstance(country.city, City)
```

## 📊 Benchmarks 

Sometimes we need to store some key value data in storages. Often it also need to be efficient for work with big data and have some validation and another features.

`django-dto-field` is a tool build around amazing [msgspec](https://github.com/jcrist/msgspec) serialization and validation library for solving this problems like a charm ✨

**DtoField vs JSONField Benchmark**

Operations on 100 000 size dict on PostgreSQL DB. Script [here](/benchmarks/jsonfield_benchmark.py).

![DtoField vs JSONField Benchmark](docs/media/bechmark.png)


## 🤗 Author

Made with love by [@skv0zsneg](https://github.com/skv0zsneg)
