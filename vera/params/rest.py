from wq.db import rest
import swapper

Site = swapper.load_model('params', 'Site')
ReportStatus = swapper.load_model('params', 'ReportStatus')
Parameter = swapper.load_model('params', 'Parameter')

rest.router.register_model(
    Site,
    lookup="slug",
)
rest.router.register_model(
    ReportStatus,
    lookup='slug',
)
rest.router.register_model(
    Parameter,
    lookup='slug',
)
