"""nps_apis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin # allows you to add admin pages to your project
from django.urls import path, include # allows you to add paths to your project and include other urls
from rest_framework import permissions # allows you to add permissions to your project
from drf_yasg.views import get_schema_view # get_schema_view allows you to returns a schema view 
from drf_yasg import openapi # openapi allows you to add swagger to your project
from django.conf import settings # 
from django.conf.urls.static import static # allows you to add static files to your project 


# below is the defining the schema view for the swagger return call
schema_view = get_schema_view(
    openapi.Info(
        title="NPS APIs",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="contact@NPS.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True, # allows you to make the swagger call public
    permission_classes=(permissions.AllowAny,), # allows you to add permissions to your project
)

# below is the url pattern for the getColumns app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userAPIs.urls')),
    #path('api/file/', include('FileUpload.urls')),
    path('api/', include('getColumns.urls')),
    #path('SentimentAnalysis/', include('NLPModel.urls')),
    #path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]


# if the settings.DEBUG is true then the below will be added to the urlpatterns
if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)