from django.contrib import admin
import core.models as core_models


@admin.register(core_models.SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'curriculum', 'id')


@admin.register(core_models.School)
class SchoolDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'curriculum', 'id')


@admin.register(core_models.Curriculum)
class CurriculumDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'id')


@admin.register(core_models.Subject)
class SubjectDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'curriculum', 'education_level', 'id')


@admin.register(core_models.College)
class CollegeDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'id')


@admin.register(core_models.Major)
class MajorDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'id')


@admin.register(core_models.MajorCategory)
class MajorCategoryDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

