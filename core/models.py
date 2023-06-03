from django.db import models
from constants import ProfileConstants

class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    

class SearchQuery(models.Model):

    class Meta:
        verbose_name_plural = "Search Queries"
    
    query = models.CharField(max_length=255, verbose_name="query")
    curriculum = models.CharField(max_length=255, verbose_name="curriculum", default=None, null=True, blank=True)
    education_level = models.CharField(max_length=255, verbose_name="education_level", default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.query}'


class School(models.Model):
    
    class Meta:
        verbose_name_plural = "School Data"
    
    name = models.CharField(max_length=255, verbose_name="name")
    address = models.CharField(max_length=255, verbose_name="address")
    curriculum = models.ForeignKey(to= Curriculum, max_length=255, verbose_name="curriculum", on_delete=models.CASCADE)
    #curriculum = models.CharField(max_length=255, verbose_name="curriculum")


    def __str__(self):
        return f'{self.name}'


class Subject(models.Model):
    
    name = models.CharField(max_length=255, verbose_name="name")
    curriculum = models.ForeignKey(to=Curriculum, verbose_name="curriculum", on_delete=models.CASCADE)
    education_level = models.CharField(max_length=255, verbose_name="education_level", choices=ProfileConstants.education_level_choices)


    class Meta:
        verbose_name_plural = "Subjects"
        unique_together = ('name', 'curriculum', 'education_level')


    def __str__(self):
        return f'{self.name}'


class College(models.Model):
    
    class Meta:
        verbose_name_plural = "College Data"
    
    name = models.CharField(max_length=255, verbose_name="name")
    address = models.CharField(max_length=255, verbose_name="country")

    def __str__(self):
        return f'{self.name}'


class MajorCategory(models.Model):
    class Meta:
        verbose_name_plural = "Major Categories"
    
    name = models.CharField(max_length=100, verbose_name="name", unique=True)

    def __str__(self):
        return self.name
    

class Major(models.Model):
    class Meta:
        verbose_name_plural = "Majors"

    name = models.CharField(verbose_name="name", max_length=100)
    category = models.ForeignKey(MajorCategory, verbose_name="category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    