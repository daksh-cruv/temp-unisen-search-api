from django.urls import include, path
from rest_framework import routers

from core.views import *

router = routers.DefaultRouter()

router.register(r"major", MajorViewSet, basename="major")
router.register(r"school", SchoolViewSet, basename="school")
router.register(r"subject", SubjectViewSet, basename="subject")
router.register(r"college", CollegeViewSet, basename="college")
router.register(r"subject/recommend", SubjectRecommendationViewSet, basename="subject_recommend")
router.register(r"major/recommend", MajorRecommendationViewSet, basename="major_recommend")

urlpatterns = [
    path("", include(router.urls)),
]