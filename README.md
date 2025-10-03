# django-dict-field

> ⚠️ This project under active developing.

Django extension for efficient and easy storing `dict` data in django field.

## 📍 Purpose

Sometimes we need to store some key value data in storages. In Django we can use `JSONField` with `json` tool to convert or `BinaryField` with some customs transformations. Often it also need to be efficient for work with big data or to have some validation and another features.

`django-dict-field` here is to solve this problems like a charm ✨

## 🚀 Quick start

1. Install `django-dict-field`.

> ⚠️ Will not work until 0.1.0 version will be realized.

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
