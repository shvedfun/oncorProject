from datetime import datetime, tzinfo, timezone, timedelta, date
import random
from pydantic import BaseModel
from .models import PopulationDistribution


class DistributionAge(BaseModel):
    age_start: int
    age_finish: int
    percent_by_population: float
    man_percent: float


class Distribution(BaseModel):
    count_people: int
    distributions: list[DistributionAge]

class DataGenerator:
    generate_point = ""

    def __init__(self, region_id):
        self.region_id = region_id

    def get_distribution(self) -> Distribution:
        distribution_row = PopulationDistribution.objects.get(region_id=self.region_id)
        # if distribution_row and distribution_row.distribution:
        return Distribution(**distribution_row.distribution)

    def generate_population(self):
        distribution = self.get_distribution()
        for dist in distribution.distributions:
            result = {}
            for i in range(int(distribution.count_people * dist.percent_by_population)):
                r4gender = random.random()
                if r4gender <= dist.man_percent:
                    result['gender'] = 'man'
                else:
                    result['gender'] = 'woman'
                delta = random.randrange(dist.age_start * 365, dist.age_finish * 365)
                result['birthday'] = date(datetime.now(tz=timezone.utc) - timedelta(days=delta))




