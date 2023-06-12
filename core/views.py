from .serializers import *
from rest_framework import views, status
from rest_framework.response import Response
from services.src import search_engine
from core.models import *
from services.subject_recommendation.subject_recommendation_system import SubjectRecommendationSystem
from services.src.major_recommendation_system import MajorRecommendationSystem


curriculum_queryset = Curriculum.objects.all()
curriculum_list = list(curriculum_queryset.values_list("abbreviation", flat=True))


school_search = search_engine.SearchEngine(School.objects.select_related('curriculum'), "school", curriculum_list)
college_search = search_engine.SearchEngine(College.objects.all(), "college")
subject_search = search_engine.SearchEngine(Subject.objects.select_related('curriculum'), "subject", curriculum_list)
major_search = search_engine.SearchEngine(Major.objects.all(), "major")
subject_recommendation = SubjectRecommendationSystem(curriculum_list, Subject.objects.select_related('curriculum'))
major_recommendation = MajorRecommendationSystem(Degree.objects.all(), Major.objects.all())


class SchoolAPIView(views.APIView):
    get_serializer_class = SchoolQuerySerializer
    post_serializer_class = SchoolDataSerializer

    """
    A simple APIView for school search and posting school data.

    The get method accepts an API call with the following parameters:
    query: the school name to search for
    curriculum: the curriculum abbreviation to filter by

    The post method accepts an API call with the following parameters:
    name: the name of the school
    address: the address of the school
    curriculum: the curriculum abbreviation of the school. Must be block letters. "CBSE", not "cbse".
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        curriculum = serializer.validated_data.get('curriculum')
        results = school_search.search(query, {'curriculum__abbreviation': curriculum.upper()})
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class SubjectAPIView(views.APIView):
    get_serializer_class = SubjectQuerySerializer
    post_serializer_class = SubjectDataSerializer

    """
    A simple APIView for getting and posting subject data.

    The get method accepts an API call with the following parameters:
    query: the subject name to search for
    curriculum: the curriculum abbreviation to filter by
    education_level: the education level to filter by, such as "ssc" or "hsc"

    The post method accepts an API call with the following parameters:
    name: the name of the subject
    curriculum: the curriculum abbreviation of the subject, must be block letters. "CBSE", not "cbse".
    education_level: the education level of the subject
    alias: the alias of the subject, such as "math" for "mathematics", or "history"
    for "Social Science"
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
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

    def post(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class CollegeAPIView(views.APIView):
    get_serializer_class = CollegeQuerySerializer
    post_serializer_class = CollegeDataSerializer

    """
    A simple APIView for getting and posting college data.

    The get method accepts an API call with the following parameters:
    query: the college name to search for

    The post method accepts an API call with the following parameters:
    name: the name of the college
    country: the country of the college
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = college_search.search(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class MajorAPIView(views.APIView):
    get_serializer_class = MajorQuerySerializer
    post_serializer_class = MajorDataSerializer

    """
    A simple APIView for getting and posting college major data.

    The get method accepts an API call with the following parameters:
    query: the major name to search for
    
    The post method accepts an API call with the following parameters:
    name: the name of the major
    category: the category of the major, such as "Engineering"
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = major_search.search(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class SaveMajorCategoryAPIView(views.APIView):
    def __init__(self):
        self.serializer_class = MajorCategorySerializer

    """
    A simple APIView for saving major category data to database.

    The post method accepts an API call with the following parameters:
    name: the name of the major category

    """

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        

class SaveCurriculumAPIView(views.APIView):
    def __init__(self):
        self.serializer_class = CurriculumDataSerializer

    """
    A simple APIView for saving curriculum data to database.

    The post method accepts an API call with the following parameters:
    name: the name of the curriculum
    abbreviation: the abbreviation of the curriculum in block letters.
    """

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class SubjectRecommendationAPIView(views.APIView):
    def __init__(self):
        self.get_serializer_class = SubjectQuerySerializer

    """
    A simple APIView for returning subject recommendations, based on the query subjects.

    The get method accepts an API call with the following parameters:
    query: the subjects to search for
    curriculum: the curriculum to filter by
    education_level: the education level to filter by
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        curriculum = serializer.validated_data.get('curriculum')
        education_level = serializer.validated_data.get('education_level')
        recommendations = subject_recommendation.recomm_logic(
                                                    query.split(", ") if query else [],
                                                    curriculum,
                                                    education_level
                                                    )
        serializer.save()
        return Response(recommendations, status=status.HTTP_200_OK)
    

class DegreeAPIView(views.APIView):
    def __init__(self):
        self.get_serializer_class = MajorQuerySerializer
        self.post_serializer_class = DegreeDataSerializer

    """
    A simple APIView for getting major recommendations based on degree and
    posting degree data.

    The get method accepts an API call with the following parameters:
    query: the degree name to get recommendations for

    The post method accepts an API call with the following parameters:
    name: the name of the degree
    education_level: the education level of the degree, such as "bachelor" or "master"
    """

    def get(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get('query')
        results = major_recommendation.get_recommendations(query)
        serializer.save()
        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.post_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    


# class DegreeAPIView(views.APIView):
#     def __init__(self):
#         self.get_serializer_class = MajorQuerySerializer
#         self.post_serializer_class = DegreeDataSerializer

#     """
#     A simple APIView for getting major recommendations based on degree and
#     posting degree data.

#     The get method accepts an API call with the following parameters:
#     query: the degree name to get recommendations for

#     The post method accepts an API call with the following parameters:
#     name: the name of the degree
#     education_level: the education level of the degree, such as "bachelor" or "master"
#     """

#     def post(self, request):
#         try:
#             data = JSONParser().parse(request)
#             serializer = self.post_serializer_class(data=data)
#             if serializer.is_valid(raise_exception=True):
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except JSONDecodeError:
#             print(serializer.errors)
#             return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
    

#     def get(self, request):
#         try:
#             data = JSONParser().parse(request)
#             serializer = self.get_serializer_class(data=data)
#             if serializer.is_valid(raise_exception=True):
#                 query = serializer.validated_data.get('query')
#                 results = major_recommendation.get_recommendations(query)
#                 serializer.save()
#                 return Response(results, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except JSONDecodeError:
#             return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)