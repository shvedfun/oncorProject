from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import DataGenerator

class Command(BaseCommand):
    help = "Generate population"

    def add_arguments(self, parser):
        parser.add_argument("region_ids", nargs="+", type=str)

    def handle(self, *args, **options):
        for region_id in options["region_ids"]:
            try:
                generator = DataGenerator(region_id)
                for pers in generator.generate_population():
                    print(pers)
            except Exception as e:
                raise e

