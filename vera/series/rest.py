from wq.db import rest
import swapper
from .serializers import EventSerializer, ReportSerializer

Event = swapper.load_model('series', 'Event')
Report = swapper.load_model('series', 'Report')

rest.router.register_model(
    Event,
    serializer=EventSerializer,
    fields="__all__",
)
rest.router.register_model(
    Report,
    serializer=ReportSerializer,
    fields="__all__",
)
