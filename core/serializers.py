from . import models
from rest_framework import serializers


class SchoolQuerySerializer(serializers.ModelSerializer):
	query = serializers.CharField(max_length=100, allow_blank=True, required=False)
	curriculum = serializers.CharField(max_length=10)

	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
			'curriculum',
		)


class SubjectQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
			'curriculum',
			'education_level'
		)


class CollegeQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
			'curriculum'
		)


class MajorQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
		)


class SchoolDataSerializer(serializers.ModelSerializer):
	curriculum = serializers.SlugRelatedField(
		queryset=models.Curriculum.objects.all(),
		slug_field='abbreviation'
	)

	class Meta:
		model = models.School
		fields = (
			'pk',
			'name',
			'address',
			'curriculum',
		)


class CurriculumDataSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Curriculum
		fields = (
			'name',
			'abbreviation'
		)


class SubjectDataSerializer(serializers.ModelSerializer):
	curriculum = serializers.SlugRelatedField(
		queryset=models.Curriculum.objects.all(),
		slug_field='abbreviation'
	)

	class Meta:
		model = models.Subject
		fields = (
			'name',
			'curriculum',
			'education_level',
			'alias'
		)


class CollegeDataSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.College
		fields = (
			'name',
			'country'
		)


class MajorDataSerializer(serializers.ModelSerializer):
	category = serializers.SlugRelatedField(
		queryset=models.MajorCategory.objects.all(),
		slug_field='name'
	)
	class Meta:
		model = models.Major
		fields = (
			'name',
			'category',
		)


class MajorCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.MajorCategory
		fields = (
			'name',
		)


class DegreeDataSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Degree
		fields = (
			'name',
			'education_level'
		)