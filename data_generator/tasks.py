from datetime import datetime, tzinfo, timezone, timedelta, date
import random
from pydantic import BaseModel
from typing import Optional
from data_generator.models import PopulationDistribution


distribution = {
  "region_code": 45,
  "date": "2023-01-01",
  "distributions": [
    {
      "age_start": 0,
      "age_finish": 4,
      "man": 19088,
      "woman": 17719
    },
    {
      "age_start": 5,
      "age_finish": 9,
      "man": 26996,
      "woman": 26117
    },
    {
      "age_start": 10,
      "age_finish": 14,
      "man": 26581,
      "woman": 24702
    },
    {
      "age_start": 15,
      "age_finish": 19,
      "man": 20668,
      "woman": 20381
    },
    {
      "age_start": 20,
      "age_finish": 24,
      "man": 16057,
      "woman": 15891
    },
    {
      "age_start": 25,
      "age_finish": 29,
      "man": 14625,
      "woman": 13777
    },
    {
      "age_start": 30,
      "age_finish": 34,
      "man": 22842,
      "woman": 22262
    },
    {
      "age_start": 35,
      "age_finish": 39,
      "man": 28469,
      "woman": 28294
    },
    {
      "age_start": 40,
      "age_finish": 44,
      "man": 25478,
      "woman": 27942
    },
    {
      "age_start": 45,
      "age_finish": 49,
      "man": 24097,
      "woman": 27895
    },
    {
      "age_start": 50,
      "age_finish": 54,
      "man": 22299,
      "woman": 26232
    },
    {
      "age_start": 55,
      "age_finish": 59,
      "man": 21975,
      "woman": 28032
    },
    {
      "age_start": 60,
      "age_finish": 64,
      "man": 26976,
      "woman": 36155
    },
    {
      "age_start": 65,
      "age_finish": 69,
      "man": 22524,
      "woman": 35029
    },
    {
      "age_start": 70,
      "age_finish": 74,
      "man": 15504,
      "woman": 28535
    },
    {
      "age_start": 75,
      "age_finish": 79,
      "man": 5355,
      "woman": 12361
    },
    {
      "age_start": 80,
      "age_finish": 84,
      "man": 4191,
      "woman": 14406
    },
    {
      "age_start": 85,
      "age_finish": 89,
      "man": 1780,
      "woman": 6858
    },
    {
      "age_start": 90,
      "age_finish": 94,
      "man": 529,
      "woman": 2417
    },
    {
      "age_start": 95,
      "age_finish": 99,
      "man": 74,
      "woman": 505
    },
    {
      "age_start": 100,
      "age_finish": 104,
      "man": 3,
      "woman": 37
    }
  ]
}




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


class DataGenerator:

    def __init__(self, region_id):
        self.region_id = region_id

    def _get_distribution_from_db(self) -> dict:
        distribution_row = PopulationDistribution.objects.get(region_id=self.region_id)
        # if distribution_row and distribution_row.distribution:
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
                result['birthday'] = (datetime.now(tz=timezone.utc) - timedelta(days=delta)).date()
                result['name'] = f'Житель-{distribution.region_code}-{dist.age_start}:{dist.age_finish}-{i + 1}'
                result['region_id'] = distribution.region_code
                yield result



