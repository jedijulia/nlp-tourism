from django.conf.urls import patterns, url

from phtweetmap.views import IndexView, RetrieveTweetsView, SetClassificationView, TestTweetsView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^retrieve/$', RetrieveTweetsView.as_view(), name='retrieve'),
    url(r'^test/$', TestTweetsView.as_view(), name='test'),
    url(r'^set/(?P<actual_classification>[\w-]+)/(?P<pk>\d+)/$', SetClassificationView.as_view(), name='set-classification'),
)