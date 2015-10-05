from wq.db import rest
from wq.db.patterns import rest as patterns
import swapper
from .serializers import EventSerializer, ReportSerializer

Site = swapper.load_model('vera', 'Site')
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')
ReportStatus = swapper.load_model('vera', 'ReportStatus')
Parameter = swapper.load_model('vera', 'Parameter')

rest.router.register_model(Site)
rest.router.register_model(Event, serializer=EventSerializer)
rest.router.register_model(Report, serializer=ReportSerializer)
rest.router.register_model(ReportStatus, lookup='slug')
rest.router.register_model(
    Parameter, serializer=patterns.IdentifiedModelSerializer
)
