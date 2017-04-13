from wq.db import rest
import swapper
from .serializers import EventSerializer, ReportSerializer


def user_filter(qs, request):
    if request.user.is_authenticated():
        return qs.filter(user=request.user)
    else:
        return qs.none()

Event = swapper.load_model('series', 'Event')
Report = swapper.load_model('series', 'Report')

rest.router.register_model(
    Event,
    serializer=EventSerializer,
    fields="__all__",
    cache="none",
)
rest.router.register_model(
    Report,
    serializer=ReportSerializer,
    fields="__all__",
    cache_filter=user_filter,
)
