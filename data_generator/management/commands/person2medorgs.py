import datetime
import json
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import task_person2medorgs

from health.models import Person, MedOrganization, Region

logger = logging.getLogger()

class Command(BaseCommand):
    help = "Raspred person to medorgs"

    def add_arguments(self, parser):
        parser.add_argument("region_ids", nargs="+", type=str)

    def handle(self, *args, **options):
        task_person2medorgs(options["region_ids"])