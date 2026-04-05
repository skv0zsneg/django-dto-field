# django-dto-field

[![PyPI version](https://img.shields.io/pypi/v/django-dto-field.svg)](https://pypi.org/project/django-dto-field/)
[![PyPI license](https://img.shields.io/pypi/l/django-dto-field.svg)](https://pypi.python.org/pypi/django-dto-field/)
[![Python Version](https://img.shields.io/pypi/pyversions/django-dto-field.svg)](https://pypi.org/project/django-dto-field/)

[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![test](https://github.com/skv0zsneg/django-dto-field/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dto-field/actions/workflows/test.yml)
[![typing & lint](https://github.com/skv0zsneg/django-dto-field/actions/workflows/typing_and_lint.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dto-field/actions/workflows/typing_and_lint.yml)

_Storing DTO data in easy-to-use and production-ready Django Model Field with fast [de]serialization._

A custom Django Model Field that can serialize and deserialize for different types of DTO (Data-Transfer-Object). `DtoField` detect DTO type and serialize the most efficiently. Also it has own binary container to maintain data integrity and economical storage. 


## ✨ Features

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

Set DTO field to your model:

```python
>>> from django.db.models import CharField
>>> from django_dto_field import DtoField

>>> class Country(Model):
...    name = CharField()
...    city = DtoField()
```

And than use it:

```python
>>> city = {"name": "Capitol", "districts": [f"d{i}" for i in range(1, 14)]}
>>> created_country = Country.objects.create(name="Panem", city=city)

>>> from_db_country = Country.objects.get(pk=created_country.pk)
>>> assert isinstance(from_db_country.city, dict)
>>> assert from_db_country.city == city
```


## 🤗 Author

Made with love by [@skv0zsneg](https://github.com/skv0zsneg)
