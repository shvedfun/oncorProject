import datetime
import json
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from data_generator.tasks import task_generate_examinations

from health.models import Person

logger = logging.getLogger()

class Command(BaseCommand):
    help = "Generate examination"

    def add_arguments(self, parser):
        parser.add_argument("region_ids", nargs="+", type=str)

    def handle(self, *args, **options):
        task_generate_examinations(options["region_ids"])
