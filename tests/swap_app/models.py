from django.db import models
from vera import base_models as vera
from django.conf import settings


class Site(vera.BaseSite):
    type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    class Meta(vera.BaseSite.Meta):
        abstract = not settings.SWAP


class Result(vera.BaseResult):
    flag = models.CharField(
        max_length=1,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = not settings.SWAP


if settings.SWAP:
    EventResult = vera.create_eventresult_model(
        event_cls=vera.Event,
        result_cls=Result,
    )
else:
    EventResult = vera.EventResult
