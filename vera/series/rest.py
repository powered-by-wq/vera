from wq.db import rest
import swapper
from .serializers import EventSerializer, ReportSerializer

Event = swapper.load_model('series', 'Event')
Report = swapper.load_model('series', 'Report')

rest.router.register_model(
    Event,
    serializer=EventSerializer,
)
rest.router.register_model(
    Report,
    serializer=ReportSerializer,
)
