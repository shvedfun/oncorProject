from django.contrib import admin

from data_generator.models import PopulationDistribution, RegionDirectionGenerateData


# Register your models here.
@admin.register(PopulationDistribution)
class PopulationDistributionAdmin(admin.ModelAdmin):
    pass


@admin.register(RegionDirectionGenerateData)
class RegionDirectionGenerateData(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(RegionDirectionGenerateData, self).get_queryset(request)
        qs = qs.select_related("region", "direction")
        return qs
