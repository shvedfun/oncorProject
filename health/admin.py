from django.contrib import admin

from health.models import (
    Region, Person, DiseaseCategory, Disease, Direction, StageDisease, PersonDisease,
    Examination, ExaminationScheme, ExaminationPlan, ExaminationFact, Applicability,
    Procedure, District, MedOrganization
)


# Register your models here.
@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    pass


@admin.register(Applicability)
class ApplicabilityAdmin(admin.ModelAdmin):
    pass


@admin.register(ExaminationFact)
class ExaminationFactAdmin(admin.ModelAdmin):
    pass

    def get_queryset(self, request):
        qs = super(ExaminationFactAdmin, self).get_queryset(request)
        qs = qs.select_related("examination", "person")
        return qs


@admin.register(ExaminationPlan)
class ExaminationPlanAdmin(admin.ModelAdmin):
    readonly_fields = ["person", "examination", ]
    list_display = ["person", "examination", "date_on"]

    def get_queryset(self, request):
        qs = super(ExaminationPlanAdmin, self).get_queryset(request)
        qs = qs.select_related("examination", "person")
        return qs


@admin.register(ExaminationScheme)
class ExaminationSchemeAdmin(admin.ModelAdmin):
    pass


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    ordering = ("code",)
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
    list_filter = ('region__code',)
    exclude = ["diseases"]


@admin.register(DiseaseCategory)
class DiseaseCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    pass


@admin.register(StageDisease)
class StageDiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonDisease)
class PersonDiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region')


@admin.register(MedOrganization)
class MedOrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'district', 'region')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.select_related("district__region")
        return qs

    def region(self, obj):
        return obj.district.region