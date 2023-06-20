from .serializers import *
from rest_framework import views, status
from rest_framework.response import Response
from services.src import search_engine
from core.models import *
from services.subject_recommendation.subject_recommendation_system import SubjectRecommendationSystem
from services.src.major_recommendation_system import MajorRecommendationSystem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets


curriculum_queryset = Curriculum.objects.all()
curriculum_list = list(curriculum_queryset.values_list("abbreviation", flat=True))


school_search = search_engine.SearchEngine(School.objects.select_related('curriculum'),
                                           "school", curriculum_list)
college_search = search_engine.SearchEngine(College.objects.all(), "college")
subject_search = search_engine.SearchEngine(Subject.objects.select_related('curriculum'),
                                            "subject", curriculum_list)
major_search = search_engine.SearchEngine(Major.objects.all(), "major")
subject_recommendation = SubjectRecommendationSystem(curriculum_list,
                                                     Subject.objects.select_related('curriculum'))
major_recommendation = MajorRecommendationSystem(Degree.objects.all(),
                                                 Major.objects.all())


class SchoolViewSet(viewsets.ViewSet):
    get_serializer_class = SchoolQuerySerializer
    post_serializer_class = SchoolDataSerializer

    """
    ViewSet for school search and posting school data.
    """

    @swagger_auto_schema(
        operation_summary='Search for schools, filtered by curriculum',
        query_serializer=SchoolQuerySerializer,
        operation_description="""
        Accepts an API call with the following parameters:
        query: the school name to search for
        curriculum: the curriculum abbreviation to filter by

        returns: a list of schools matching the query with the following attributes:
        name (str): the name of the school
        address (str): the address of the school
        match_score (float): the match score of the school
        """,
        responses={
            200: openapi.Response(
                description='A list of schools matching the query',
                examples={
                    'application/json': [
                        [
                            'School Name 1',
                            'School Address 1',
                            'Match Score 1'
                        ],
                        [
                            'School Name 2',
                            'School Address 2',
                            'Match Score 2'
                        ]
                    ]
                }
            )
        },
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        curriculum = serializer.validated_data.get('curriculum')
        results = school_search.search(query, {'curriculum__abbreviation': curriculum.upper()})
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=SchoolDataSerializer,
        operation_summary='Post school data',
        operation_description="""
        Accepts an API call with the following parameters:
        name: the name of the school
        address: the address of the school
        curriculum: the curriculum abbreviation of the school.
        """,
        responses={
            201: SchoolDataSerializer
        }
    )
    def create(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubjectViewSet(viewsets.ViewSet):
    education_level_choices = [choice[0] for choice in ProfileConstants.education_level_choices]

    get_serializer_class = SubjectQuerySerializer
    post_serializer_class = SubjectDataSerializer

    """
    ViewSet for getting and posting subject data.
    """

    @swagger_auto_schema(
        operation_summary='Search for subjects, filtered by curriculum and education level',
        query_serializer=SubjectQuerySerializer,
        manual_parameters=[
            openapi.Parameter(
                name='education_level',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='The education level to filter by, such as "ssc" or "hsc"',
                enum=education_level_choices,
            )
        ],
        operation_description="""
        Accepts an API call with the following parameters:
        query: the subject name to search for
        curriculum: the curriculum abbreviation to filter by
        education_level: the education level to filter by, such as "ssc" or "hsc"

        returns: a list of subjects matching the query with the following attributes:
        name (str): the name of the subject
        match_score (float): the match score of the subject
        """,
        responses={
            200: openapi.Response(
                description='A list of subjects matching the query',
                examples={
                    'application/json': [
                        [
                            'Subject Name 1',
                            'Match Score 1'
                        ],
                        [
                            'Subject Name 2',
                            'Match Score 2'
                        ]
                    ]
                }
            )
        },
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        curriculum = serializer.validated_data.get('curriculum')
        education_level = serializer.validated_data.get('education_level')
        results = subject_search.search(query,
                                        {'curriculum__abbreviation': curriculum.upper(),
                                         'education_level': education_level.lower()
                                         },
                                        subject=True)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=SubjectDataSerializer,
        operation_summary='Post subject data',
        operation_description="""
        Accepts an API call with the following parameters:
        name: the name of the subject.
        curriculum: the curriculum abbreviation of the subject, must be block letters.
        For example, "CBSE", not "cbse" or "Cbse".
        education_level: the education level of the subject.
        alias: the alias of the subject, such as "math" for "mathematics", or "history"
               for "Social Science".
        """,
        responses={
            201: SubjectDataSerializer
        }
    )
    def create(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CollegeViewSet(viewsets.ViewSet):
    get_serializer_class = CollegeQuerySerializer
    post_serializer_class = CollegeDataSerializer

    """
    ViewSet for getting and posting college data.
    """

    @swagger_auto_schema(
        operation_summary = 'Search for colleges',
        query_serializer = CollegeQuerySerializer,
        operation_description="""
        Accepts an API call with the following parameters:
        query: the college name to search for

        returns: a list of colleges matching the query with the following attributes:
        name (str): the name of the college
        match_score (float): the match score of the college
        """,
        responses={
            200: openapi.Response(
                description='A list of colleges matching the query',
                examples={
                    'application/json': [
                        [
                            'College Name 1',
                            'Match Score 1'
                        ],
                        [
                            'College Name 2',
                            'Match Score 2'
                        ]
                    ]
                }
            )
        },
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = college_search.search(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=CollegeDataSerializer,
        operation_summary='Post college data',
        operation_description="""
        Accepts an API call with the following parameters:
        name: the name of the college
        country: the country of the college
        """,
        responses={
            201: CollegeDataSerializer
        }
    )
    def create(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MajorViewSet(viewsets.ViewSet):
    get_serializer_class = MajorQuerySerializer
    post_serializer_class = MajorDataSerializer

    """
    ViewSet for getting and posting college major data.
    """

    @swagger_auto_schema(
            operation_summary='Search for majors',
            query_serializer=MajorQuerySerializer,
            operation_description="""
            Accepts an API call with the following parameters:
            query: the major name to search for
            """,
            responses={
                200: openapi.Response(
                    description='A list of majors matching the query',
                    examples={
                        'application/json': [
                            [
                            'Major Name 1',
                            'Match Score 1'
                            ],
                            [
                            'Major Name 2',
                            'Match Score 2'
                            ]
                        ]
                    }
                )
            },
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = major_search.search(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)

    @swagger_auto_schema(
            operation_summary='Post major data',
            request_body=MajorDataSerializer,
            operation_description="""
            Accepts an API call with the following parameters:
            name: the name of the major
            category: the category of the major, such as "Engineering"
            """,
            responses={
                201: MajorDataSerializer
            },
    )
    def create(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubjectRecommendationViewSet(viewsets.ViewSet):
    education_level_choices = [choice[0] for choice in ProfileConstants.education_level_choices]
    get_serializer_class = SubjectQuerySerializer

    """
    ViewSet for returning subject recommendations, based on the query subjects,
    curriculum, and education level.
    """

    @swagger_auto_schema(
        operation_summary='Get subject recommendations, based on the query subjects, curriculum, and education level',
        query_serializer=SubjectQuerySerializer,
        manual_parameters=[
            openapi.Parameter(
                name='education_level',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='The education level to filter by, such as "ssc" or "hsc"',
                enum=education_level_choices,
            )
        ],
        operation_description="""
        Accepts an API call with the following parameters:
        query: the subjects to search for
        curriculum: the curriculum to filter by
        education_level: the education level to filter by

        returns: a list of recommended subjects.
        """,
        responses={
            200: openapi.Response(
                description="Subject recommendations successfully returned",
                examples={
                    "application/json": [
                        "Subject 1",
                        "Subject 2",
                        "Subject 3"
                    ]
                }
            )
        }
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        curriculum = serializer.validated_data.get('curriculum')
        education_level = serializer.validated_data.get('education_level')
        recommendations = subject_recommendation.recomm_logic(
            [subject.title() for subject in query.split(", ")] if query else [],
            curriculum.upper(),
            education_level
        )
        serializer.save()
        return Response(recommendations, status=status.HTTP_200_OK)

    
class MajorRecommendationViewSet(viewsets.ViewSet):
    get_serializer_class = MajorQuerySerializer

    """
    ViewSet for getting major recommendations based on degree and posting degree data.
    """

    @swagger_auto_schema(
        operation_summary='Get major recommendations, based on the query degree',
        query_serializer=MajorQuerySerializer,
        operation_description="""
        Accepts an API call with the following parameters:
        query: the degree to search for
        """,
        responses={
            200: openapi.Response(
                description="Major recommendations successfully returned",
                examples={
                    "application/json": [
                        "Major 1",
                        "Major 2",
                        "Major 3"
                    ]
                }
            )
        }
    )
    def list(self, request):
        serializer = self.get_serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = major_recommendation.get_recommendations(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)