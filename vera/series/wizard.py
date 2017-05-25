from data_wizard import registry
from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from wq.db.patterns import serializers as patterns
from .serializers import ReportSerializer
from vera.results.serializers import SettableField, ValueValidator
import swapper
from django.conf import settings


Report = swapper.load_model('series', 'Report')
ReportStatus = swapper.load_model('params', 'ReportStatus')
Result = swapper.load_model('results', 'Result')


class DefaultStatus(serializers.Serializer):
    status_id = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=ReportStatus.objects.all(),
        default=getattr(settings, 'WQ_DEFAULT_REPORT_STATUS', None),
    )


# EAV serializer for "wide" spreadsheets
class ReportSerializer(ReportSerializer, DefaultStatus):
    class Meta:
        model = Report
        fields = "__all__"


# Single result per row for "tall" spreadsheets
class SingleResultSerializer(ModelSerializer):
    value = SettableField()

    class Meta:
        exclude = ('report', 'value_text', 'value_numeric', 'empty')
        model = Result
        validators = [ValueValidator()]


class ReportResultSerializer(
        patterns.NaturalKeyModelSerializer, DefaultStatus):
    result = SingleResultSerializer(many=False)

    def create(self, validated_data):
        result_data = validated_data.pop('result')
        report = super(ReportResultSerializer, self).create(validated_data)
        result_data['report'] = report
        SingleResultSerializer().create(result_data)
        return report

    class Meta:
        model = Report
        fields = '__all__'


registry.register("Report Series (Wide)", ReportSerializer)
registry.register("Result Series (Tall)", ReportResultSerializer)
