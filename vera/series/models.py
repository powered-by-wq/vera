from django.db import models
from natural_keys import NaturalKeyModel
from wq.db.patterns.models import LabelModel
import swapper
from django.utils.timezone import now
from django.conf import settings
from collections import OrderedDict

swapper.set_app_prefix('series', 'WQ')

VALID_REPORT_ORDER = getattr(settings, "WQ_VALID_REPORT_ORDER", ('-entered',))
# Base classes for Event-Report pattern
# Extend these when swapping out default implementation (below)


class BaseEvent(NaturalKeyModel, LabelModel):
    site = models.ForeignKey(
        swapper.get_model_name('params', 'Site'),
        null=True, blank=True, related_name="event_set",
    )

    @property
    def valid_reports(self):
        return self.report_set.filter(status__is_valid=True).order_by(
            *VALID_REPORT_ORDER
        )

    @property
    def vals(self):
        return OrderedDict([
            (a.type.natural_key()[0], a.value)
            for a in self.results
        ])

    # Valid results for this event
    @property
    def results(self):
        Result = swapper.load_model('results', 'Result')
        return Result.objects.valid_results(report__event=self)

    @property
    def is_valid(self):
        return self.valid_reports.count() > 0

    wq_label_template = "{{site.slug}} Event"

    class Meta:
        abstract = True


class ReportManager(models.Manager):
    def create_report(self, event_key, values, **kwargs):
        Event = swapper.load_model('series', 'Event')
        kwargs['event'] = Event.objects.find(*event_key)
        report = self.create(**kwargs)
        report.vals = values
        return report


class ValidReportManager(ReportManager):
    def get_queryset(self):
        qs = super(ValidReportManager, self).get_queryset()
        return qs.filter(status__is_valid=True).order_by(*VALID_REPORT_ORDER)


class BaseReport(LabelModel):
    event = models.ForeignKey(
        swapper.get_model_name('series', 'Event'),
        related_name="report_set"
    )
    entered = models.DateTimeField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        swapper.get_model_name('params', 'ReportStatus'),
        null=True,
        blank=True
    )

    objects = ReportManager()
    valid_objects = ValidReportManager()

    @property
    def is_valid(self):
        return self.status and self.status.is_valid

    @property
    def vals(self):
        vals = OrderedDict()
        for result in self.results.all():
            vals[result.type.natural_key()[0]] = result.value
        return vals

    @vals.setter
    def vals(self, vals):
        Parameter = swapper.load_model('params', 'Parameter')
        keys = [(key,) for key in vals.keys()]
        params, success = Parameter.objects.resolve_keys(keys)
        if not success:
            missing = [
                name for name, resolved in params.items() if resolved is None
            ]
            raise TypeError(
                "Could not identify one or more parameters: %s!"
                % missing
            )

        for key, param in params.items():
            result, is_new = self.results.get_or_create(type=param)
            result.value = vals[key[0]]
            result.save()

    def save(self, *args, **kwargs):
        if not self.entered:
            self.entered = now()
        super(BaseReport, self).save(*args, **kwargs)

    wq_label_template = (
        "{{#event}}Report for {{site.slug}} Event{{/event}}"
        "{{^event}}New Report{{/event}}"
    )

    class Meta:
        abstract = True
        ordering = VALID_REPORT_ORDER


# Default implementation of the above classes, can be swapped
class Event(BaseEvent):
    date = models.DateField()

    wq_label_template = "{{site.slug}} on {{date}}"

    class Meta(BaseEvent.Meta):
        db_table = 'wq_event'
        swappable = swapper.swappable_setting('series', 'Event')
        unique_together = ('site', 'date')
        ordering = ('-date',)


class Report(BaseReport):
    wq_label_template = (
        "{{#event}}Report for {{site.slug}} on {{date}}{{/event}}"
        "{{^event}}New Report{{/event}}"
    )

    class Meta(BaseReport.Meta):
        db_table = 'wq_report'
        swappable = swapper.swappable_setting('series', 'Report')
