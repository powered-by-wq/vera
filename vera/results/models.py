from django.db import models
import swapper
from django.db.models.signals import post_save
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import receiver
from django.utils.six import string_types
from .compat import clone_field


from vera.series.models import (
    Event,
    BaseEvent,
    BaseReport,
    VALID_REPORT_ORDER
)

swapper.set_app_prefix('results', 'WQ')


# Base classes for Result and EventResult
# Extend these when swapping out default implementation (below)

class ResultManager(models.Manager):
    def valid_results(self, **filter):
        Parameter = swapper.load_model('params', 'Parameter')

        filter['report__status__is_valid'] = True
        filter['empty'] = False

        # DISTINCT ON event, then parameter, collapsing results from different
        # reports into one
        distinct = ['report__event__id'] + nest_ordering(
            'type', Parameter._meta.ordering
        ) + ['type__id']

        # ORDER BY distinct fields, then valid report order
        order = distinct + nest_ordering('report', VALID_REPORT_ORDER)

        return self.filter(
            **filter
        ).order_by(*order).distinct(*distinct).select_related('report')


class BaseResult(models.Model):
    type = models.ForeignKey(swapper.get_model_name('params', 'Parameter'))
    report = models.ForeignKey(
        swapper.get_model_name('series', 'Report'),
        related_name='results'
    )
    value_numeric = models.FloatField(null=True, blank=True)
    value_text = models.TextField(null=True, blank=True)
    empty = models.BooleanField(default=False, db_index=True)

    objects = ResultManager()

    def is_empty(self, value):
        if value is None:
            return True
        if isinstance(value, string_types) and len(value.strip()) == 0:
            return True
        return False

    @property
    def value(self):
        if self.type.is_numeric:
            return self.value_numeric
        return self.value_text

    @value.setter
    def value(self, val):
        self.empty = self.is_empty(val)
        if self.type.is_numeric:
            if self.empty:
                self.value_numeric = None
            else:
                self.value_numeric = val
        else:
            self.value_text = val

    def __str__(self):
        return "%s -> %s: %s" % (self.report, self.type, self.value)

    class Meta:
        abstract = True
        ordering = ('type',)
        index_together = [
            ('type', 'report', 'empty'),
        ]


# Denormalize Events with Results from valid Reports
class EventResultManager(models.Manager):
    def set_for_event(self, event, delete=True):
        """
        Update EventResult cache for the given event.
        """
        if delete:
            self.filter(event=event).delete()
        for result in event.results:
            er = self.model(
                event=event,
                result=result
            )
            er.save()

    def set_for_events(self, delete=True, **event_filter):
        """
        Update EventResult cache for the given events.  The event query should
        be specified as query keyword arguments, rather than a queryset, so
        that a JOIN can be used instead of retrieving the results for each
        event separately.
        """

        # Delete existing EventResults (using denormalized Event fields)
        if delete:
            er_filter = {
                'event_' + key: val for key, val in event_filter.items()
            }
            self.filter(**er_filter).delete()

        # Filter results (using JOIN through Report to Event)
        Result = swapper.load_model('results', 'Result')
        result_filter = {
            'report__event__' + key: val for key, val in event_filter.items()
        }
        ers = []
        results = Result.objects.valid_results(
            **result_filter
        ).select_related('report__event')
        for result in results:
            er = self.model(
                event=result.report.event,
                result=result
            )
            er.denormalize()
            ers.append(er)
        self.bulk_create(ers)

    def set_all(self):
        """
        Reset the entire EventResult cache.
        """
        self.set_for_events()


class BaseEventResult(models.Model):
    """
    Denormalized event-result pairs (for valid reports)
    """
    id = models.PositiveIntegerField(primary_key=True)
    event = models.ForeignKey(swapper.get_model_name('series', 'Event'))
    result = models.ForeignKey(swapper.get_model_name('results', 'Result'))
    objects = EventResultManager()

    @property
    def result_value(self):
        if self.result_type.is_numeric:
            return self.result_value_numeric
        return self.result_value_text

    def __str__(self):
        return "%s -> %s: %s" % (
            self.event,
            self.result_type,
            self.result_value
        )

    def save(self, *args, **kwargs):
        if self.event_id is None or self.result_id is None:
            return
        self.denormalize()
        super(BaseEventResult, self).save(*args, **kwargs)

    def denormalize(self):
        """
        Denormalize all properties from the event and the result.
        """
        self.pk = self.result.pk

        def set_value(src, field):
            if field.primary_key:
                return
            name = field.name
            if field.rel:
                name += "_id"
            obj = getattr(self, src)
            setattr(self, src + '_' + name, getattr(obj, name))

        for field in self.event._meta.fields:
            set_value('event', field)
        for field in self.result._meta.fields:
            set_value('result', field)

    class Meta:
        abstract = True


def create_eventresult_model(event_cls, result_cls,
                             base=BaseEventResult, swappable=False):
    """
    **Here be magic**

    EventResult needs to have all of the fields from Event and Result.
    In order to DRY (and since either of these classes may be swapped), we
    add the fields dynamically here.  If neither Event or Result are swapped,
    this function will be called below, otherwise the user should call
    this function in their models.py.
    """

    app = 'results'
    module = base.__module__
    for cls in event_cls, result_cls, base:
        if cls._meta.app_label not in ('series', 'results'):
            app = cls._meta.app_label
            module = cls.__module__

    class Meta(base.Meta):
        db_table = 'wq_eventresult'
        unique_together = ('event', 'result_type')
        app_label = app

    if swappable:
        Meta.swappable = swappable

    attrs = {
        'Meta': Meta,
        '__module__': module
    }

    def add_field(prefix, field):
        if field.primary_key:
            return
        attrs[prefix + '_' + field.name] = clone_field(field)

    for field in event_cls._meta.fields:
        add_field('event', field)

    for field in result_cls._meta.fields:
        add_field('result', field)

    EventResult = type(
        'EventResult',
        (base,),
        attrs
    )

    # Disconnect any existing receiver
    post_save.disconnect(dispatch_uid="eventresult_receiver")

    @receiver(post_save, weak=False, dispatch_uid="eventresult_receiver")
    def handler(sender, instance=None, **kwargs):
        event = find_event(instance)
        if event:
            EventResult.objects.set_for_event(event)

    return EventResult


# Default implementation of the above classes, can be swapped
class Result(BaseResult):
    class Meta(BaseResult.Meta):
        db_table = 'wq_result'
        swappable = swapper.swappable_setting('results', 'Result')


EventResult = create_eventresult_model(
    Event, Result,
    swappable=swapper.swappable_setting('results', 'EventResult')
)

if ((swapper.is_swapped('series', 'Event')
        or swapper.is_swapped('results', 'Result'))
        and not swapper.is_swapped('results', 'EventResult')):
    raise ImproperlyConfigured(
        "Event or Result was swapped but EventResult was not!"
    )


def nest_ordering(prefix, ordering, ignore_reverse=False):
    nest_order = []
    for field in ordering:
        reverse = ''
        if field.startswith('-'):
            field = field[1:]
            if not ignore_reverse:
                reverse = '-'
        nest_order.append(reverse + prefix + '__' + field)
    return nest_order


def find_event(instance):
    if isinstance(instance, BaseEvent):
        return instance
    if isinstance(instance, BaseReport):
        return instance.event
    if isinstance(instance, BaseResult):
        return instance.report.event
    return None
