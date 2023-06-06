from . import models
from rest_framework import serializers
from rest_framework.fields import CharField
from services.src import search_engine



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
	
	# def save(self):
	# 	query = self.validated_data.get('query')
	# 	curriculum = self.validated_data.get('curriculum')
	# 	results = search.search(query, curriculum, subject_or_major=True)
	# 	return results


class CollegeQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
			'curriculum'
		)
	
	# def save(self):
	# 	query = self.validated_data.get('query')
	# 	results = search.search(query)
	# 	return results


class MajorQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.SearchQuery
		fields = (
			'query',
		)
	
	# def save(self):
	# 	query = self.validated_data.get('query')
	# 	results = search.search(query, subject_or_major=True)
	# 	return results


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
			'curriculum'
		)


class CurriculumSerializer(serializers.ModelSerializer):
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
			'education_level'
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