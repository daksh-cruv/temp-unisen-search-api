from django.db import models
from constants import ProfileConstants

class Curriculum(models.Model):

    """
    Stores the different curriculums in the database.
    Attributes:
        name (str): The full name of the curriculum.
        abbreviation (str): The abbreviation of the curriculum.
    """
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    

class SearchQuery(models.Model):

    """
    Stores the search queries in the database.
    Attributes:
        query (str): The search query received in API calls (can be null).
        curriculum (str): The curriculum of the search query (can be null).
        education_level (str): The education level of the search query (can be null).
    """

    class Meta:
        verbose_name_plural = "Search Queries"
    
    query = models.CharField(max_length=255)
    curriculum = models.CharField(max_length=255, default=None, null=True, blank=True)
    education_level = models.CharField(max_length=255, default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.query}'


class School(models.Model):
    
    """
    Stores the different schools in the database.
    Attributes:
        name (str): The full name of the school.
        address (str): The address of the school.
        curriculum (str): The curriculum of the school. It is a foreign key to the Curriculum model.
    """
    class Meta:
        verbose_name_plural = "School Data"
    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    curriculum = models.ForeignKey(to= Curriculum, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.name}'


class Subject(models.Model):
    
    """
    Stores the different subjects in the database.
    Attributes:
        name (str): The full name of the subject.
        curriculum (str): The curriculum of the subject. It is a foreign key to the Curriculum model.
        education_level (str): The education level of the subject, such as ssc or hsc.
        alias (str): The alias of the subject, such as math or mathematics, or history and sst for
        social science.
    """
    name = models.CharField(max_length=255)
    curriculum = models.ForeignKey(to=Curriculum, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=255, choices=ProfileConstants.education_level_choices)
    alias = models.CharField(max_length=255, null=True, blank=True)



    class Meta:
        verbose_name_plural = "Subjects"
        unique_together = ('name', 'curriculum', 'education_level')


    def __str__(self):
        return f'{self.name}'


class College(models.Model):
    
    """
    Stores the different colleges in the database.
    Attributes:
        name (str): The full name of the college.
        country (str): The address of the college.
    """
    class Meta:
        verbose_name_plural = "College Data"
    
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class MajorCategory(models.Model):

    """
    Stores the different major categories in the database.
    Attributes:
        name (str): The full name of the major category.
    """
    class Meta:
        verbose_name_plural = "Major Categories"
    
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Major(models.Model):

    """
    Stores the different majors in the database.
    Attributes:
        name (str): The full name of the major.
        category (str): The category of the major. It is a foreign key to the MajorCategory model.
    """
    class Meta:
        verbose_name_plural = "Majors"

    name = models.CharField("name", max_length=100)
    category = models.ForeignKey(MajorCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Degree(models.Model):

    """
    Stores the different college degrees in the database.
    Attributes:
        name (str): The full name of the degree.
        education_level (str): The education level of the degree, such as bachelor or master.
    """
    name = models.CharField(max_length=100)
    education_level = models.CharField(max_length=10, choices=ProfileConstants.college_education_choices)

    def __str__(self):
        return self.name