from rest_framework import serializers
from wq.db.patterns import serializers as patterns
from wq.db.rest.serializers import ModelSerializer
from vera.results.serializers import ResultSerializer


class EventSerializer(ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        list_exclude = ('results',)


class ReportSerializer(patterns.NaturalKeyAttachedModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True)

    def to_internal_value(self, data):
        data = data.copy()
        if 'request' in self.context and not data.get('user_id', None):
            user = self.context['request'].user
            if user.is_authenticated():
                data['user_id'] = user.pk
        return super(ReportSerializer, self).to_internal_value(data)
