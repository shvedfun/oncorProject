import logging

from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import DataGenerator

from health.models import Person

logger = logging.getLogger()

class Command(BaseCommand):
    help = "Generate population"

    def add_arguments(self, parser):
        parser.add_argument("region_ids", nargs="+", type=str)

    def handle(self, *args, **options):
        for region_id in options["region_ids"]:
            try:
                # delete region population
                Person.objects.filter(region_id=region_id).delete()
                # Create region population
                persons = []
                generator = DataGenerator(region_id)
                for pers in generator.generate_population():
                    logger.debug(pers)
                    person = Person(**pers)
                    persons.append(person)
                    if len(persons) >= 100:
                        Person.objects.bulk_create(persons)
                        persons = []
                if persons:
                    Person.objects.bulk_create(persons)

            except Exception as e:
                raise e

