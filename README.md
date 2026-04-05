# django-dto-field

[![PyPI version](https://img.shields.io/pypi/v/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)
[![PyPI license](https://img.shields.io/pypi/l/django-dict-field.svg)](https://pypi.python.org/pypi/django-dict-field/)
[![Python Version](https://img.shields.io/pypi/pyversions/django-dict-field.svg)](https://pypi.org/project/django-dict-field/)

[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![test](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/test.yml)
[![typing & lint](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml/badge.svg?event=push)](https://github.com/skv0zsneg/django-dict-field/actions/workflows/typing_and_lint.yml)

Storing DTO data in Django model field with fast [de]serialization.

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
