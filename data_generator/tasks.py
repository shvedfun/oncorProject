import datetime
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
                # logger.debug(f'scrining = {scrining}')
                scrining: ExaminationScheme = scrining
                if (
                        scrining.gender == 'all' or scrining.gender == person.gender
                ):
                    if (
                            (age + self.plan_horizont) >=
                            scrining.age[0] and (age < scrining.age[1])
                    ):
                        for add_year in range(self.plan_horizont):
                            # logger.debug(f'add_year = {add_year}')
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
            # logger.debug(f'person = {person}')
            person: Person = person
            result = PersonExaminationPlan(person_id=person.id, plan=[])
            result.plan = self.get_examinations_to_person(person, target_date)
            if result.plan:
                yield result


def task_generate_examinations(region_ids: list):
    for region_id in region_ids:
        try:
            #
            persons_qs = Person.objects.filter(region_id=region_id).order_by('id')

            qs = RegionDirectionGenerateData.objects.filter(
                region_id=region_id,
                type=GenerateDataType.plan
            ).order_by('-load_date')

            for direction in Direction.objects.all():
                logger.debug(f'Обрабатываю направление: {direction}')
                row = qs.filter(direction_id=direction.id).first()
                if row:
                    schemas = row.data
                    # with open(os.getcwd() + "\\data_generator\\scrinning.json", mode="r", encoding="utf-8") as f:
                    #     schemas = json.loads(f.read())
                    schemas = DirectionScriningsSchemas(**schemas)
                    generator = ExaminationPlanGenerator(person_queryset=persons_qs, schemas=schemas)
                    for pers in generator.generate_by_person(date.fromisoformat("2024-07-01")):
                        logger.debug(f'pers = {pers}')
                        with atomic():
                            person = Person.objects.get(pk=pers.person_id)
                            # delete exam plan for person
                            ExaminationPlan.objects.filter(person_id=person.id).delete()
                            add2plan = []
                            for examination in pers.plan:
                                try:
                                    # logger.debug(f'examination = {examination}')
                                    disease = Disease.objects.get(name__iexact=examination.disease)
                                    age = examination.date.year - person.birthday.year
                                    exam = Examination.objects.filter(
                                        disease_id=disease.id,
                                        applicability__from_age__lte=age,
                                        applicability__to_age__gte=age
                                    ).first()
                                    if exam:
                                        ex_plan = ExaminationPlan(
                                            person_id=person.id, examination=exam, date_on=examination.date
                                        )
                                        logger.debug(f'add ex_plan {ex_plan}, age = {age}')
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
        # logger.debug(f'qs = {qs_in.values()[:3]}')
        results = qs_in.values_list("person_id", flat=True)
        results = list(results)
        # logger.debug(f'len(results) = {len(results)}')
        k = int(len(results) * factor)
        results = random.sample(results, k=k)
        # logger.debug(f'len(results) = {len(results)}')
        saveed_n = 0
        for plan in qs_in.filter(person_id__in=results):
            if saveed_n == 0:
                logger.debug(f'plan = {plan.examination.disease.name}')
            ExaminationFact.objects.create(
                person_id=plan.person_id, examination_id=plan.examination_id,
                date=plan.date_on, examination_plan_id=plan.id
            )
            saveed_n += 1
        logger.debug(f'create fact from plan N = {saveed_n}')


    def _generate_fact_by_distribution(self, qs_in: QuerySet, distribution: FactDistribution):
        qs_common = qs_in.filter(
            old__gte=distribution.age_start,
            old__lte=distribution.age_finish
        )
        # logger.debug(f'qs_common[:3] = {qs_common.values()[:3]}')
        for factor in distribution.factors:
            disease_id = Disease.objects.get(name__iexact=factor.disease)
            qs_disease = qs_common.filter(examination__disease_id=disease_id)
            # logger.debug(f'qs_disease[] = {qs_disease.values()[:3]}')
            if factor.man > 0:
                qs_man = qs_disease.filter(person__gender=GenderEnum.MAN)
                # logger.debug(f'qs_man[] = {qs_man.values()[:3]}')
                self._generate_fact_by_plan(qs_man, factor.man)
            if factor.woman > 0:
                qs_woman = qs_disease.filter(person__gender=GenderEnum.WOMAN)
                # logger.debug(f'qs_woman[] = {qs_woman.values()[:3]}')
                self._generate_fact_by_plan(qs_woman, factor.woman)

    def _generate_fact_by_fullscheme(self, scheme4fact: Scheme4FactGenerator):
        direction_id = Direction.objects.get(name__iexact=scheme4fact.direction)
        # logger.debug(f'scheme4fact = {scheme4fact}')
        ExaminationFact.objects.filter(
            person__region_id=str(scheme4fact.region_code),
            examination__disease__direction_id=direction_id,
            date__gte=date(scheme4fact.year, 1, 1),
            date__lte=date(scheme4fact.year, 12, 31)
        ).delete()

        qs = ExaminationPlan.objects.select_related(
            "examination__disease__direction", "person"
        ).filter(
            person__region__code=str(scheme4fact.region_code),
            examination__disease__direction_id=direction_id,
            date_on__gte=date(scheme4fact.year, 1, 1),
            date_on__lte=date(scheme4fact.year, 12, 31)
        ).annotate(
            old = ExtractYear("date_on") - ExtractYear("person__birthday")
            # old=ExtractYear(
            #     ExpressionWrapper(
            #         Coalesce((F("date_on") - F("person__birthday")), datetime.timedelta(days=1)),
            #         output_field=DurationField
            #     )
            # ) # ExtractYear(
        )
        logger.debug(f'gs[:3] = {qs.values()[:3]}')
        for dist in scheme4fact.distributions:
            # logger.debug(f'dist = {dist}')
            self._generate_fact_by_distribution(qs, dist)


    def generate_fact(self):
        scheme4facts = self.get_json4generation()
        for scheme4fact in scheme4facts:
            if scheme4fact.year <=0:
                scheme4fact.year = self.year
            self._generate_fact_by_fullscheme(scheme4fact)



