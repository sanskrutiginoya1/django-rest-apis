from django.conf.urls import url
from .views import UploadFileView
from django.views.decorators.csrf import csrf_exempt
# from .views import MyUploadView
urlpatterns = [
    url('', UploadFileView.as_view(), name='file-upload'),
    #    url('',MyUploadView.as_view(), name='file-upload'),
    #url('data/', csrf_exempt(dataget_list.as_view()), name='data')
]
