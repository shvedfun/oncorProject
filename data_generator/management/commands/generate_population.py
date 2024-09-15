import logging

from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import generate_population


logger = logging.getLogger()

class Command(BaseCommand):
    help = "Generate population"

    def add_arguments(self, parser):
        parser.add_argument("region_ids", nargs="+", type=str)

    def handle(self, *args, **options):
        generate_population(options["region_ids"])