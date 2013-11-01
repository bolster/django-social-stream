from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.http import HttpResponse


def callback(request):
    return HttpResponse("")


urlpatterns = patterns(
    '',
    url(r'callback/', callback, name="callback")
)
