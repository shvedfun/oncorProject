from django.contrib import admin

from data_generator.models import PopulationDistribution
# Register your models here.
@admin.register(PopulationDistribution)
class PopulationDistributionAdmin(admin.ModelAdmin):
    pass