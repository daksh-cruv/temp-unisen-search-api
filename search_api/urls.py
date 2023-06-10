from django.urls import path
from django.contrib import admin
from core import views as core_views
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns += [
    path('admin/', admin.site.urls),
    path('profile/school', core_views.SchoolAPIView.as_view()),
    path('profile/school/subject', core_views.SubjectAPIView.as_view()),
    path('profile/college', core_views.CollegeAPIView.as_view()),
    path('profile/college/major', core_views.MajorAPIView.as_view()),
    path('profile/save/curriculum', core_views.SaveCurriculumAPIView.as_view()),
    path('profile/save/majorcategory', core_views.SaveMajorCategoryAPIView.as_view()),
    path('profile/school/subject/recommend', core_views.SubjectRecommendationAPIView.as_view()),
    path('profile/college/major/recommend', core_views.DegreeAPIView.as_view()),
    path('profile/save/degree', core_views.DegreeAPIView.as_view()),
]