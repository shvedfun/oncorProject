from django.contrib import admin

from health.models import Region, Person

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    ordering = ("code",)
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
    list_filter = ('region__code',)