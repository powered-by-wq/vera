from wq.db import rest
import swapper
from .serializers import EventSerializer, ReportSerializer

Event = swapper.load_model('series', 'Event')
Report = swapper.load_model('series', 'Report')

rest.router.register_model(
    Event,
    serializer=EventSerializer,
    fields="__all__",

    max_local_pages=1,
    partial=True,
    reversed=True,
)
rest.router.register_model(
    Report,
    serializer=ReportSerializer,
    fields="__all__",

    max_local_pages=1,
    partial=True,
    reversed=True,
)
