from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional


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
    distributions: List[DistributionAge]


class ExaminationScheme(BaseModel):
    gender: str
    age: List[int]
    periodicity: float
    examination: str


class DiseaseSchemas(BaseModel):
    disease: str
    schemas: List[ExaminationScheme]


class DirectionScriningsSchemas(BaseModel):
    direction: str
    scrinings: List[dict]


class ExaminationWithDate(BaseModel):
    disease: str
    examination: str
    date: date


class PersonExaminationPlan(BaseModel):
    person_id: int
    plan: List[ExaminationWithDate]


class FactFactor(BaseModel):
    disease: str
    man: Optional[float] = -1.0
    woman: Optional[float] = -1.0


class FactDistribution(BaseModel):
    age_start: int = None
    age_finish: int =None
    factors: Optional[List[FactFactor]] = []


class Scheme4FactGenerator(BaseModel):
    region_code: int
    date: date
    direction: str
    year: Optional[int] = -1
    distributions: List[FactDistribution]
