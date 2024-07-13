import os
import json
import logging
from datetime import datetime, timedelta, date
import random
from dateutil.relativedelta import relativedelta

from django.db.models import QuerySet
from django.utils import timezone

from data_generator.models import PopulationDistribution
from data_generator.data_scheme import Distribution, DistributionAge, \
    ExaminationScheme, DiseaseSchemas, DirectionScriningsSchemas, PersonExaminationPlan, ExaminationWithDate

from health.models import Person

logger = logging.getLogger()

# distribution4del = {
#   "region_code": 45,
#   "date": "2023-01-01",
#   "distributions": [
#     {
#       "age_start": 0,
#       "age_finish": 4,
#       "man": 19088,
#       "woman": 17719
#     },
#     {
#       "age_start": 5,
#       "age_finish": 9,
#       "man": 26996,
#       "woman": 26117
#     },
#     {
#       "age_start": 10,
#       "age_finish": 14,
#       "man": 26581,
#       "woman": 24702
#     },
#     {
#       "age_start": 15,
#       "age_finish": 19,
#       "man": 20668,
#       "woman": 20381
#     },
#     {
#       "age_start": 20,
#       "age_finish": 24,
#       "man": 16057,
#       "woman": 15891
#     },
#     {
#       "age_start": 25,
#       "age_finish": 29,
#       "man": 14625,
#       "woman": 13777
#     },
#     {
#       "age_start": 30,
#       "age_finish": 34,
#       "man": 22842,
#       "woman": 22262
#     },
#     {
#       "age_start": 35,
#       "age_finish": 39,
#       "man": 28469,
#       "woman": 28294
#     },
#     {
#       "age_start": 40,
#       "age_finish": 44,
#       "man": 25478,
#       "woman": 27942
#     },
#     {
#       "age_start": 45,
#       "age_finish": 49,
#       "man": 24097,
#       "woman": 27895
#     },
#     {
#       "age_start": 50,
#       "age_finish": 54,
#       "man": 22299,
#       "woman": 26232
#     },
#     {
#       "age_start": 55,
#       "age_finish": 59,
#       "man": 21975,
#       "woman": 28032
#     },
#     {
#       "age_start": 60,
#       "age_finish": 64,
#       "man": 26976,
#       "woman": 36155
#     },
#     {
#       "age_start": 65,
#       "age_finish": 69,
#       "man": 22524,
#       "woman": 35029
#     },
#     {
#       "age_start": 70,
#       "age_finish": 74,
#       "man": 15504,
#       "woman": 28535
#     },
#     {
#       "age_start": 75,
#       "age_finish": 79,
#       "man": 5355,
#       "woman": 12361
#     },
#     {
#       "age_start": 80,
#       "age_finish": 84,
#       "man": 4191,
#       "woman": 14406
#     },
#     {
#       "age_start": 85,
#       "age_finish": 89,
#       "man": 1780,
#       "woman": 6858
#     },
#     {
#       "age_start": 90,
#       "age_finish": 94,
#       "man": 529,
#       "woman": 2417
#     },
#     {
#       "age_start": 95,
#       "age_finish": 99,
#       "man": 74,
#       "woman": 505
#     },
#     {
#       "age_start": 100,
#       "age_finish": 104,
#       "man": 3,
#       "woman": 37
#     }
#   ]
# }


class PopulationDataGenerator:

    def __init__(self, region_code):
        self.region_code = region_code

    def _get_distribution_from_db(self) -> dict:
        distribution_row = PopulationDistribution.objects.get(region_id=self.region_code)
        return distribution_row.distribution


    def _normalize_distribution(self, distribution: DistributionAge) -> DistributionAge:
        return distribution

    def generate_population(self):
        distribution = Distribution(**self._get_distribution_from_db())
        for dist in distribution.distributions:
            result = {}
            dist = self._normalize_distribution(dist)
            for i in range(dist.man + dist.woman):
                if i < dist.man:
                    result['gender'] = 'М'
                else:
                    result['gender'] = 'Ж'
                delta = random.randrange(dist.age_start * 365, dist.age_finish * 365)
                result['birthday'] = (timezone.now() - timedelta(days=delta)).date()
                result['name'] = f'Житель-{distribution.region_code}-{dist.age_start}:{dist.age_finish}-{i + 1}'
                result['region_id'] = distribution.region_code
                yield result


def generate_population(region_ids: list):
    for region_id in region_ids:
        try:
            # delete region population
            Person.objects.filter(region_id=region_id).delete()
            # Create region population
            persons = []
            generator = PopulationDataGenerator(region_id)
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


class ExaminationPlanGenerator:
    """"
    Для каждой персоны из queryset генерируются обследования по схеме из schemas
    """

    def __init__(self, person_queryset: QuerySet, schemas: DirectionScriningsSchemas, plan_horizont: int = 5):
        self.queryset: QuerySet = person_queryset
        self.schemas = schemas
        self.plan_horizont = plan_horizont

    def get_years(self, tmdlt: timedelta) -> int:
        return tmdlt // timedelta(days=365.25)

    def get_examinations_to_person(self, person: Person, target_date: date) -> list[ExaminationWithDate]:
        result = []
        for scrinings in self.schemas.scrinings:
            # logger.debug(f'scrinings = {scrinings}')
            scrinings = DiseaseSchemas(**scrinings)
            for scrining in scrinings.schemas:
                logger.debug(f'scrining = {scrining}')
                scrining: ExaminationScheme = scrining
                if (
                        scrining.gender == 'all' or scrining.gender == person.gender
                ):
                    if (
                            (person.age + self.plan_horizont) >= scrining.age[0] and (person.age < scrining.age[1])
                    ):
                        for add_year in range(self.plan_horizont):
                            logger.debug(f'add_year = {add_year}')
                            if (person.age + add_year >= scrining.age[0]) \
                                    and (person.age + add_year < scrining.age[1]) \
                                    and ((person.age + add_year - scrining.age[0]) % scrining.periodicity == 0):
                                new_ex_plan = ExaminationWithDate(
                                    date=person.birthday + relativedelta(years=person.age + add_year),
                                    disease=scrinings.disease,
                                    examination=scrining.examination
                                )
                                logger.debug(f'append = {new_ex_plan}')
                                result.append(new_ex_plan)
        return result

    def generate_by_person(self, target_date: date):
        for person in self.queryset[:100]: #.prefetch_related("examination_plan_from_person")
            logger.debug(f'person = {person}')
            person: Person = person
            person.age = self.get_years(target_date - person.birthday)  # TODO
            logger.debug(f'person_age = {person.age}')
            result = PersonExaminationPlan(person_id=person.id, plan=[])
            result.plan = self.get_examinations_to_person(person, target_date)
            if result.plan:
                yield result


def task_generate_examinations(region_ids: list):
    for region_id in region_ids:
        try:
            # delete region population
            persons_qs = Person.objects.filter(region_id=region_id).order_by(
                '-id'
            ).filter(
                birthday__gt=timezone.now() - timedelta(days=365.25 * 50),
                birthday__lt=timezone.now() - timedelta(days=365.25 * 45)
            )
            # Create region population
            persons = []
            logger.debug(f'cur wd = {os.getcwd()}')
            with open(os.getcwd() + "\\data_generator\\scrinning.json", mode="r", encoding="utf-8") as f:
                schemas = json.loads(f.read())
            schemas = DirectionScriningsSchemas(**schemas)
            generator = ExaminationPlanGenerator(person_queryset=persons_qs, schemas=schemas)
            for pers in generator.generate_by_person(date.fromisoformat("2024-07-01")):
                logger.debug(pers)
            #     person = Person(**pers)
            #     persons.append(person)
            #     if len(persons) >= 100:
            #         Person.objects.bulk_create(persons)
            #         persons = []
            # if persons:
            #     Person.objects.bulk_create(persons)
            #
        except Exception as e:
            raise e







