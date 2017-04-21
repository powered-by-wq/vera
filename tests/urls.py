from django.conf.urls import include, url
from wq.db import rest
from vera.results import views
from rest_framework.urlpatterns import format_suffix_patterns


def make_urls(views):
    urls = [
        url(r'^(?P<ids>[^\.]+)/' + name + '$', cls.as_view())
        for name, cls in views.items()
    ]
    return format_suffix_patterns(urls)


chart_urls = make_urls({
    'timeseries': views.TimeSeriesView,
    'scatter': views.ScatterView,
    'boxplot': views.BoxPlotView,
})

urlpatterns = [
    url(r'^',       include(rest.router.urls)),
    url(r'^chart',  include(chart_urls))
]
