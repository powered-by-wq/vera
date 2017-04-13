from wq.db import rest
from wq.db.patterns import serializers as patterns
import swapper

Site = swapper.load_model('params', 'Site')
ReportStatus = swapper.load_model('params', 'ReportStatus')
Parameter = swapper.load_model('params', 'Parameter')

rest.router.register_model(
    Site,
    serializer=patterns.IdentifiedModelSerializer,
    fields="__all__",
    cache="all",
)
rest.router.register_model(
    ReportStatus,
    serializer=patterns.IdentifiedModelSerializer,
    fields="__all__",
    cache="all",
)
rest.router.register_model(
    Parameter,
    serializer=patterns.IdentifiedModelSerializer,
    fields="__all__",
    cache="all",
)
