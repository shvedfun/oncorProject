import datetime
import json
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import task_generate_examinations, task_fact_raspred

from health.models import Person, MedOrganization, Region

logger = logging.getLogger()

class Command(BaseCommand):
    help = "Generate fact"

    def add_arguments(self, parser):
        parser.add_argument("region_id", type=int)
        parser.add_argument("year", type=int)
        parser.add_argument("direction_id", type=int)

    def handle(self, *args, **options):
        task_fact_raspred(options["region_id"], options["year"], options["direction_id"])