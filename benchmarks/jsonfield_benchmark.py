import os
import random
import sys
import timeit

import django
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment
from tabulate import tabulate

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
django_app_path = os.path.join(project_root, "tests", "django_app")

sys.path.insert(0, project_root)
sys.path.insert(0, django_app_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
django.setup()

setup_test_environment()
db_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

from dict_field.models import ModelForTest

DICT_SIZE = 100_000
BIG_DICT = {str(i): i for i in range(DICT_SIZE)}


def get_big_dict_field(test_model: ModelForTest, field_name: str) -> None:
    rand_index = str(random.randint(0, DICT_SIZE - 1))
    test_model = ModelForTest.objects.get(pk=test_model.pk)
    test_model.__getattribute__(field_name)[rand_index]


def delete_big_dict_field(test_model: ModelForTest, field_name: str) -> None:
    rand_index = str(random.randint(0, DICT_SIZE - 1))
    val = test_model.__getattribute__(field_name)[rand_index]
    del test_model.__getattribute__(field_name)[rand_index]
    test_model.save()
    # NOTE: Here is overhead because of saving deleted value. Must to figure
    # out how to test delete correctly.
    test_model.__getattribute__(field_name)[rand_index] = val
    test_model.save()


def update_big_dict_field(test_model: ModelForTest, field_name: str) -> None:
    rand_index = str(random.randint(0, DICT_SIZE - 1))
    test_model.__getattribute__(field_name)[rand_index] = "restored"
    test_model.save()


def run_bench():
    # NOTE: Can take a while. Be careful.
    number = 1000
    test_model_jsonfield = ModelForTest.objects.create(
        default_json_field=BIG_DICT, default_dict_field={}
    )
    test_model_dictfield = ModelForTest.objects.create(
        default_json_field={}, default_dict_field=BIG_DICT
    )

    # JSONField
    time_to_get = timeit.timeit(
        lambda: get_big_dict_field(test_model_jsonfield, "default_json_field"),
        number=number,
    )
    time_to_delete = timeit.timeit(
        lambda: delete_big_dict_field(test_model_jsonfield, "default_json_field"),
        number=number,
    )
    time_to_update = timeit.timeit(
        lambda: update_big_dict_field(test_model_jsonfield, "default_json_field"),
        number=number,
    )
    json_field_time = ("JSONField", time_to_get, time_to_update, time_to_delete)

    # DictField
    time_to_get = timeit.timeit(
        lambda: get_big_dict_field(test_model_dictfield, "default_dict_field"),
        number=number,
    )
    time_to_delete = timeit.timeit(
        lambda: delete_big_dict_field(test_model_dictfield, "default_dict_field"),
        number=number,
    )
    time_to_update = timeit.timeit(
        lambda: update_big_dict_field(test_model_dictfield, "default_dict_field"),
        number=number,
    )
    dict_field_time = ("DictField", time_to_get, time_to_update, time_to_delete)

    report_table = tabulate(
        (json_field_time, dict_field_time),
        headers=("Field", "Get", "Delete", "Update"),
        tablefmt="grid",
    )
    print(report_table)


if __name__ == "__main__":
    try:
        run_bench()
    finally:
        teardown_test_environment()
        connection.creation.destroy_test_db(db_name, verbosity=1)
