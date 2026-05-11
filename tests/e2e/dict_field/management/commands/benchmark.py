import time
from typing import Any

from tabulate import tabulate
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Model

from dict_field.models import BenchmarkModel


class Command(BaseCommand):
    help = "Run benchmark for DTOField and JSONField"

    def handle(self, *args, **kwargs):
        self.run_migration()

        self.stdout.write(self.style.WARNING("Generate test data..."))
        test_data = self.generate_test_data()
        BenchmarkModel.objects.all().delete()

        self.stdout.write(self.style.WARNING("Starting benchmark..."))
        json_write_time, json_read_time = self.benchmark_field(
            BenchmarkModel,
            "json_field",
            test_data,
        )
        dto_write_time, dto_read_time = self.benchmark_field(
            BenchmarkModel,
            "dto_field",
            test_data,
        )
        self.stdout.write(self.style.SUCCESS("Benchmark end!"))
        self.print_benchmark_results(json_write_time, json_read_time, dto_write_time, dto_read_time)

    def generate_test_data(self, times: int = 10_000):
        data_list = []
        for i in range(times):
            data = {
                "key1": f"value{i}",
                "key2": i * i,
                "nested_dict": {"nested_key": "nested_value" for _ in range(i)},
                "list": ["list_val" for _ in range(i)],
            }
            data_list.append(data)
        return data_list

    def benchmark_field(self, model: type[Model], field_name: str, test_data: list[dict[str, Any]]):
        write_times = []
        read_times = []

        for data in test_data:
            instance = model()

            start_time = time.perf_counter()
            setattr(instance, field_name, data)
            instance.save()
            end_time = time.perf_counter()
            write_times.append(end_time - start_time)

            saved_instance = model.objects.get(id=instance.id)

            start_time = time.perf_counter()
            getattr(saved_instance, field_name)
            end_time = time.perf_counter()
            read_times.append(end_time - start_time)

        write_time = (sum(write_times) / len(write_times)) * 1000
        read_time = (sum(read_times) / len(read_times)) * 1000
        return write_time, read_time

    def run_migration(self):
        self.stdout.write("Running migrations...")
        call_command("migrate", verbosity=0)
        self.stdout.write("Migrations completed.")

    def print_benchmark_results(
        self, json_write_time, json_read_time, dto_write_time, dto_read_time
    ):
        data = [
            ["Write Time", f"{json_write_time:.6f} ms", f"{dto_write_time:.6f} ms"],
            ["Read Time", f"{json_read_time:.6f} ms", f"{dto_read_time:.6f} ms"],
        ]
        headers = ["Field", "JSONField", "DTOField"]

        table = tabulate(data, headers=headers, tablefmt="grid")
        self.stdout.write(table)
