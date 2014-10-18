from wq.db.contrib.chart import views as chart
from .serializers import EventResultSerializer

import swapper
EventResult = swapper.load_model('vera', 'EventResult')


class ChartView(chart.ChartView):
    model = EventResult
    serializer_class = EventResultSerializer
    exclude_apps = ['dbio']

    def get_queryset(self):
        qs = super(ChartView, self).get_queryset()
        qs = qs.select_related('event_site', 'result_type')
        return qs

    def filter_by_site(self, qs, ids):
        return qs.filter(event_site__in=ids)

    def filter_by_parameter(self, qs, ids):
        return qs.filter(result_type__in=ids)


class TimeSeriesView(ChartView, chart.TimeSeriesMixin):
    pass


class ScatterView(ChartView, chart.ScatterMixin):
    pass


class BoxPlotView(ChartView, chart.BoxPlotMixin):
    pass
