from django.urls import path, include
from django.contrib import admin
from core import views as core_views
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers


schema_view = get_schema_view(
   openapi.Info(
      title="Unisen Search API",
      default_version='v1',
      description="API for Unisen's school, college, subject, and major data.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', include('core.urls')),
#    path('profile/school', core_views.SchoolAPIView.as_view()),
#    path('profile/school/subject', core_views.SubjectAPIView.as_view()),
#    path('profile/college', core_views.CollegeAPIView.as_view()),
#    path('profile/college/major', core_views.MajorAPIView.as_view()),
#    path('profile/save/curriculum', core_views.SaveCurriculumAPIView.as_view()),
#    path('profile/save/majorcategory', core_views.SaveMajorCategoryAPIView.as_view()),
#    path('profile/school/subject/recommend', core_views.SubjectRecommendationAPIView.as_view()),
#    path('profile/college/major/recommend', core_views.DegreeAPIView.as_view()),
#    path('profile/save/degree', core_views.DegreeAPIView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]