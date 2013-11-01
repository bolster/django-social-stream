from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns(
    '',
    url(r'^twitter/', include('social_stream.twitter.urls', namespace="twitter")),
    url(r'^facebook/', include('social_stream.facebook.urls', namespace="facebook")),
)
