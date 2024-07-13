from datetime import date
from pydantic import BaseModel
from typing import List


class DistributionAge(BaseModel):
    age_start: int
    age_finish: int
    man: int = -1
    woman: int = -1
    percent_by_population: float = -1
    man_percent: float = -1


class Distribution(BaseModel):
    date: date
    count_people: int = -1
    region_code: int = -1
    distributions: list[DistributionAge]


class ExaminationScheme(BaseModel):
    gender: str
    age: list[int]
    periodicity: float
    examination: str


class DiseaseSchemas(BaseModel):
    disease: str
    schemas: list[ExaminationScheme]


class DirectionScriningsSchemas(BaseModel):
    direction: str
    scrinings: list[dict]


class ExaminationWithDate(BaseModel):
    disease: str
    examination: str
    date: date


class PersonExaminationPlan(BaseModel):
    person_id: int
    plan: list[ExaminationWithDate]

