from rest_framework import serializers
from wq.db.patterns import serializers as patterns
from wq.db.rest.serializers import ModelSerializer


import swapper
Event = swapper.load_model('vera', 'Event')
Parameter = swapper.load_model('vera', 'Parameter')
Result = swapper.load_model('vera', 'Result')
EventResult = swapper.load_model('vera', 'EventResult')


class SettableField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, value):
        return value


class ResultSerializer(patterns.TypedAttachmentSerializer):
    value = SettableField()
    object_field = 'report'
    type_model = Parameter

    def to_representation(self, obj):
        result = super(ResultSerializer, self).to_representation(obj)
        if getattr(obj.type, 'units', None) is not None:
            result['units'] = obj.type.units
        return result

    class Meta(patterns.TypedAttachmentSerializer.Meta):
        exclude = ('report', 'value_text', 'value_numeric')
        model = Result


class EventSerializer(ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        list_exclude = ('results',)


class ReportSerializer(patterns.NaturalKeyModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True)

    def to_internal_value(self, data):
        data = data.copy()
        if 'request' in self.context and not data.get('user_id', None):
            user = self.context['request'].user
            if user.is_authenticated():
                data['user_id'] = user.pk
        return super(ReportSerializer, self).to_internal_value(data)


class EventResultSerializer(serializers.Serializer):
    site = serializers.ReadOnlyField(
        source='event_site.primary_identifier.slug'
    )
    date = serializers.ReadOnlyField(
        source='event_date'
    )
    parameter = serializers.ReadOnlyField(
        source='result_type.primary_identifier.slug'
    )
    units = serializers.ReadOnlyField(
        source='result_type.units'
    )
    value = serializers.ReadOnlyField(
        source='result_value'
    )

    class Meta:
        pandas_index = ['date']
        pandas_unstacked_header = ['site', 'parameter', 'units']
        pandas_scatter_coord = ['units', 'parameter']
        pandas_scatter_header = ['site']
        pandas_boxplot_group = 'site'
        pandas_boxplot_date = 'date'
        pandas_boxplot_header = ['units', 'parameter']
