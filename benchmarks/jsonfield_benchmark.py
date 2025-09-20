import os
import random
import sys
import timeit

import django
from tabulate import tabulate

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
django_app_path = os.path.join(project_root, 'tests', 'django_app')

sys.path.insert(0, project_root)
sys.path.insert(0, django_app_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

# Инициализируем Django
django.setup()

from dict_field.models import ModelForTest

DICT_SIZE = 100_000
BIG_DICT = {str(i): i for i in range(DICT_SIZE)}


def crud_on_big_dict_field(test_model: ModelForTest, field_name: str) -> None:
    """Function for testing CRUD operations for `DictFiled` and `JSONField`."""
    rand_index = str(random.randint(0, DICT_SIZE - 1))
    # get
    test_model.__getattribute__(field_name)[rand_index]
    # delete
    del test_model.__getattribute__(field_name)[rand_index]
    test_model.save()
    # update
    test_model.__getattribute__(field_name)[rand_index] = "restored"
    test_model.save()


if __name__ == "__main__":
    test_model_jsonfield = ModelForTest.objects.create(
        default_json_field=BIG_DICT, default_dict_field={}
    )
    time_for_jsonfield = timeit.timeit(
        lambda: crud_on_big_dict_field(test_model_jsonfield, "default_json_field"),
        number=100,
    )

    test_model_dictfield = ModelForTest.objects.create(
        default_json_field={}, default_dict_field=BIG_DICT
    )
    time_for_dictfield = timeit.timeit(
        lambda: crud_on_big_dict_field(test_model_dictfield, "default_dict_field"),
        number=100,
    )

    report_table = tabulate(
        [
            ["Time for JSONField", time_for_jsonfield],
            ["Time for DictField", time_for_dictfield],
        ]
    )
    print(report_table)
