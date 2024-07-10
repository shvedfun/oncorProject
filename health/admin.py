from django.contrib import admin

from health.models import Region, Person, DiseaseCategory, Disease, Direction, StageDisease, PersonDisease

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    ordering = ("code",)
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
    list_filter = ('region__code',)


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
