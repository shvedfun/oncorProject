import os
import json
import logging
import traceback
from datetime import timedelta, date
import random
from dateutil.relativedelta import relativedelta
from typing import List

from django.db.models import QuerySet, F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractYear, Coalesce
from django.db.transaction import atomic
from django.utils import timezone


from data_generator.models import PopulationDistribution, RegionDirectionGenerateData, GenerateDataType
from data_generator.data_scheme import (
    Distribution, DistributionAge, ExaminationScheme, DiseaseSchemas, DirectionScriningsSchemas,
    PersonExaminationPlan, ExaminationWithDate, Scheme4FactGenerator, FactDistribution
)

from health.models import Person, Disease, Examination, ExaminationPlan, ExaminationFact, Direction, GenderEnum

logger = logging.getLogger()


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


    def get_examinations_to_person(self, person: Person, target_date: date) -> list[ExaminationWithDate]:
        result = []
        age = person.age(target_date)
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
                            (age + self.plan_horizont) >=
                            scrining.age[0] and (age < scrining.age[1])
                    ):
                        for add_year in range(self.plan_horizont):
                            logger.debug(f'add_year = {add_year}')
                            if (age + add_year >= scrining.age[0]) \
                                    and (age + add_year < scrining.age[1]) \
                                    and ((age + add_year - scrining.age[0]) % scrining.periodicity == 0):
                                new_ex_plan = ExaminationWithDate(
                                    date=person.birthday + relativedelta(years=age + add_year),
                                    disease=scrinings.disease,
                                    examination=scrining.examination
                                )
                                logger.debug(f'append = {new_ex_plan}')
                                result.append(new_ex_plan)
        return result

    def generate_by_person(self, target_date: date):
        for person in self.queryset.iterator(chunk_size=100): #.prefetch_related("examination_plan_from_person")
            logger.debug(f'person = {person}')
            person: Person = person
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
                with atomic():
                    add2plan = []
                    person_id = pers.person_id
                    for examination in pers.plan:
                        try:
                            logger.debug(f'examination = {examination}')
                            disease = Disease.objects.get(name__iexact=examination.disease)
                            exam = Examination.objects.get(disease_id=disease.id)
                            ex_plan = ExaminationPlan(person_id=person_id, examination=exam, date=examination.date)
                            add2plan.append(ex_plan)
                        except Exception as e:
                            logger.error(f'Error = {e} : {traceback.format_exc()}')
                    ExaminationPlan.objects.bulk_create(add2plan)

        except Exception as e:
            raise e


class ExaminationFactGenerator:

    def __init__(self, region_id: int, year: int, direction_id: int = None):
        self.region_id = region_id
        self.year = year
        self.direction_id = direction_id

    def get_json4generation(self) -> List[Scheme4FactGenerator]:
        datas = RegionDirectionGenerateData.objects.filter(
            is_active=True, region_id=self.region_id, year=self.year, type=GenerateDataType.fact
        ).order_by("-load_date")

        if self.direction_id is not None:
            datas = datas.filter(direction_id=self.direction_id)

        results = []
        for dt in datas.iterator():
            result = Scheme4FactGenerator(**dt.data)
            results.append(result)
        return results

    def _generate_fact_by_plan(self, qs_in, factor):
        logger.debug(f'qs = {qs_in.query}')
        results = qs_in.values_list("person_id", flat=True)
        k = int(qs_in.count() * factor)
        results = random.sample(results, k=k)
        for plan in qs_in.filter(person_id__in=results):
            fact = ExaminationFact.objects.create(
                person_id=plan.person_id, examination_id=plan.examination_id,
                date=plan.date_on, examination_plan_id=plan.id
            )
            logger.debug(f'create fact = {fact}')


    def _generate_fact_by_distribution(self, qs_in: QuerySet, distribution: FactDistribution):
        qs_common = qs_in.filter(
            old__gte=distribution.age_start,
            old__lte=distribution.age_finish
        )
        for factor in distribution.factors:
            qs_disease = qs_common.filter(examination__disease__name__iexact=factor.disease)
            if factor.man > 0:
                self._generate_fact_by_plan(qs_disease.filter(person__gender=GenderEnum.MAN), factor.man)
            if factor.woman > 0:
                self._generate_fact_by_plan(qs_disease.filter(person__gender=GenderEnum.MAN), factor.woman)

    def _generate_fact_by_fullscheme(self, scheme4fact: Scheme4FactGenerator):
        direction_id = Direction.objects.get(name__iexact=scheme4fact.direction)
        logger.debug(f'scheme4fact = {scheme4fact}')
        ExaminationFact.objects.filter(
            person__region_id=str(scheme4fact.region_code),
            examination__disease__direction_id=direction_id,
            date__gte=date(scheme4fact.year, 1, 1),
            date__lte=date(scheme4fact.year, 12, 31)
        ).delete()

        qs = ExaminationPlan.objects.select_related(
            "examination__disease__direction", "person"
        ).filter(
            person__region_id=str(scheme4fact.region_code),
            examination__disease__direction_id=direction_id,
            date_on__gte=date(scheme4fact.year, 1, 1),
            date_on__lte=date(scheme4fact.year, 12, 31)
        ).annotate(
            old=ExtractYear(
                Coalesce(
                    ExpressionWrapper(F("date_on") - F("person__birthday"), output_field=DurationField()),
                    DurationField(0)
                )
            ) # ExtractYear(
        )

        for dist in scheme4fact.distributions:
            logger.debug(f'dist = {dist}')
            self._generate_fact_by_distribution(qs, dist)


    def generate_fact(self):
        scheme4facts = self.get_json4generation()
        for scheme4fact in scheme4facts:
            if scheme4fact.year <=0:
                scheme4fact.year = self.year
            self._generate_fact_by_fullscheme(scheme4fact)



