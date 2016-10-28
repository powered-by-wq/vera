from django.db import models
from wq.db.patterns import models as patterns
import swapper

swapper.set_app_prefix('params', 'WQ')


# Base metadata classes (Site, ReportStatus, Parameter)
class BaseSite(patterns.IdentifiedModel):
    @property
    def valid_events(self):
        events = self.event_set.filter(
            report_set__status__is_valid=True
        ).values_list('pk', flat=True)
        # FIXME: events may be duplicated
        return self.event_set.filter(pk__in=events)

    class Meta(patterns.IdentifiedModel.Meta):
        abstract = True


class BaseReportStatus(patterns.IdentifiedModel):
    is_valid = models.BooleanField(default=False)

    class Meta(patterns.IdentifiedModel.Meta):
        abstract = True


class BaseParameter(patterns.IdentifiedModel):
    is_numeric = models.BooleanField(default=False)
    units = models.CharField(max_length=50, null=True, blank=True)

    wq_label_template = "{{name}}{{#units}} ({{units}}){{/units}}"

    class Meta(patterns.IdentifiedModel.Meta):
        abstract = True


# Default implementation of the above classes, can be swapped
class Site(BaseSite):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta(BaseSite.Meta):
        db_table = 'wq_site'
        swappable = swapper.swappable_setting('params', 'Site')


class ReportStatus(BaseReportStatus):
    class Meta(BaseReportStatus.Meta):
        verbose_name_plural = 'report statuses'
        db_table = 'wq_reportstatus'
        swappable = swapper.swappable_setting('params', 'ReportStatus')


class Parameter(BaseParameter):
    class Meta(BaseParameter.Meta):
        db_table = 'wq_parameter'
        swappable = swapper.swappable_setting('params', 'Parameter')
