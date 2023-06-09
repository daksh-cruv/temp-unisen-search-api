from json import JSONDecodeError
from django.http import JsonResponse
from .serializers import *
from rest_framework.parsers import JSONParser
from rest_framework import views, status
from rest_framework.response import Response
from services.src import search_engine
from core.models import *


curriculum_queryset = Curriculum.objects.all()
curriculum_list = list(curriculum_queryset.values_list("abbreviation", flat=True))


school_search = search_engine.SearchEngine(School.objects.select_related('curriculum'), "school", curriculum_list)
college_search = search_engine.SearchEngine(College.objects.all(), "college")
subject_search = search_engine.SearchEngine(Subject.objects.select_related('curriculum'), "subject", curriculum_list)
major_search = search_engine.SearchEngine(Major.objects.all(), "major")


class SchoolAPIView(views.APIView):
    get_serializer_class = SchoolQuerySerializer
    post_serializer_class = SchoolDataSerializer

    """
    A simple APIView for school search and posting school data.
    """

    def get(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.get_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                # pass the first argument as the query and the second as filter_dictionary
                query = serializer.validated_data.get('query')
                # all arguments after query are passed as filter_dictionary
                curriculum = serializer.validated_data.get('curriculum')
                results = school_search.search(query, {'curriculum__abbreviation': curriculum.upper()}) 
                serializer.save()
                return Response(results, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

    # keep this above for now
    
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.post_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


class SubjectAPIView(views.APIView):
    get_serializer_class = SubjectQuerySerializer
    post_serializer_class = SubjectDataSerializer

    """
    A simple APIView for creating search entires.
    """

    def get(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.get_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                query = serializer.validated_data.get('query')
                curriculum = serializer.validated_data.get('curriculum')
                education_level = serializer.validated_data.get('education_level')
                results = subject_search.search(query,
                                                {'curriculum__abbreviation': curriculum.upper(),},
                                                subject=True)
                serializer.save()
                return Response(results, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.post_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


class CollegeAPIView(views.APIView):
    get_serializer_class = CollegeQuerySerializer
    post_serializer_class = CollegeDataSerializer

    """
    A simple APIView for creating search entires.
    """

    def get(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.get_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                query = serializer.validated_data.get('query')
                results = college_search.search(query)
                serializer.save()
                return Response(results, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
        

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.post_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

        

class MajorAPIView(views.APIView):
    get_serializer_class = MajorQuerySerializer
    post_serializer_class = MajorDataSerializer

    """
    A simple APIView for creating search entires.
    """

    def get(self, request):
            try:
                data = JSONParser().parse(request)
                serializer = self.get_serializer_class(data=data)
                if serializer.is_valid(raise_exception=True):
                    query = serializer.validated_data.get('query')
                    results = major_search.search(query)
                    serializer.save()
                    return Response(results, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except JSONDecodeError:
                return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.post_serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


class SaveMajorCategoryAPIView(views.APIView):
    def __init__(self):
        self.serializer_class = MajorCategorySerializer

    """
    A simple APIView for saving school data to database.
    """

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
        

class SaveCurriculumAPIView(views.APIView):
    def __init__(self):
        self.serializer_class = CurriculumSerializer

    """
    A simple APIView for saving school data to database.
    """

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            print(serializer.errors)
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

