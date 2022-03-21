from .views import * # import all views
from django.urls import path # import path


# below is the url pattern for the getColumns app
urlpatterns = [
    path('xml-file/', xmlfileview.as_view(), name='xml-file'),
    path('file/', File_uploadview.as_view(), name='file'),
    path('db/', DbConnect.as_view(), name='dbconnect'),
    path('dbfield/', getdbFields.as_view(), name='dbfield'),
    path('getcategory/', getCategoryValues.as_view(), name='getcategory'),
]