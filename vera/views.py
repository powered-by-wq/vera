from rest_pandas import (
    PandasView, PandasUnstackedSerializer, PandasScatterSerializer,
    PandasBoxplotSerializer,
)
from .serializers import EventResultSerializer
from .filters import ChartFilterBackend


import swapper
EventResult = swapper.load_model('vera', 'EventResult')


class ChartView(PandasView):
    queryset = EventResult.objects.all()
    serializer_class = EventResultSerializer
    filter_backends = [ChartFilterBackend]

    def get_queryset(self):
        qs = super(ChartView, self).get_queryset()
        qs = qs.select_related('event_site', 'result_type')
        return qs


class TimeSeriesView(ChartView):
    pandas_serializer_class = PandasUnstackedSerializer


class ScatterView(ChartView):
    pandas_serializer_class = PandasScatterSerializer


class BoxPlotView(ChartView):
    pandas_serializer_class = PandasBoxplotSerializer
